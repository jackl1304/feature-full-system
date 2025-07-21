# src/models/db.py

import os
from typing import Generator, List, Dict, Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import update

# Datenbank-URL
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
    link: str = Field(index=True)       # nur index, kein unique
    published: datetime
    source: str
    is_sent: bool = Field(default=False)

def init_db() -> None:
    """
    Legt alle Tabellen an, falls sie noch nicht existieren.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Liefert eine DB-Session für FastAPI-Dependencies.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def save_articles(items: List[Dict]) -> None:
    """
    Speichert neue Artikel, überspringt bereits vorhandene Links.
    """
    with Session(engine) as session:
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

def get_unsent_articles() -> List[Dict]:
    """
    Liest alle Artikel, die noch nicht versendet wurden.
    """
    with Session(engine) as session:
        articles = session.exec(
            select(Article).where(Article.is_sent == False)
        ).all()
        return [article.dict() for article in articles]

def mark_as_sent(ids: List[int]) -> None:
    """
    Markiert Artikel als versendet anhand ihrer IDs.
    """
    with Session(engine) as session:
        session.exec(
            update(Article).where(Article.id.in_(ids)).values(is_sent=True)
        )
        session.commit()
