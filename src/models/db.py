# src/models/db.py

import os
from typing import Generator, List, Dict, Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import update

# Datenbank-URL aus Umgebungsvariable oder Default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/news.db")

# Engine konfigurieren
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

class Article(SQLModel, table=True):
    """
    Repräsentiert einen News-Artikel.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str = Field(index=True, unique=True)
    published: datetime
    source: str
    is_sent: bool = Field(default=False)

def init_db() -> None:
    """
    Legt alle Tabellen an, falls sie noch nicht existieren.
    """
    from .user import User, Subscription
    from .log import FetchLog
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Liefert eine synchronisierte DB-Session (für FastAPI-Dependencies).
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

async def save_articles(items: List[Dict]) -> None:
    """
    Speichert neue Artikel; überspringt bereits vorhandene (unique link).
    """
    session = Session(engine)
    try:
        for item in items:
            exists = session.exec(
                select(Article).where(Article.link == item["link"])
            ).first()
            if exists:
                continue
            article = Article(
                title=item["title"],
                link=item["link"],
                published=item["published"],
                source=item["source"]
            )
            session.add(article)
        session.commit()
    finally:
        session.close()

async def get_unsent_articles() -> List[Dict]:
    """
    Gibt alle noch nicht versendeten Artikel als Liste von Dicts zurück.
    """
    session = Session(engine)
    try:
        articles = session.exec(
            select(Article).where(Article.is_sent == False)
        ).all()
        return [article.dict() for article in articles]
    finally:
        session.close()

async def mark_as_sent(ids: List[int]) -> None:
    """
    Markiert die Artikel mit den gegebenen IDs als versendet.
    """
    session = Session(engine)
    try:
        session.exec(
            update(Article).where(Article.id.in_(ids)).values(is_sent=True)
        )
        session.commit()
    finally:
        session.close()
