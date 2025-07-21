import os
from sqlmodel import SQLModel, create_engine
from sqlmodel import Session
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/news.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    """
    Erstellt alle Tabellen, falls nicht vorhanden.
    """
    from models.user import User, Subscription
    from models.log import FetchLog
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Liefert eine DB-Session für FastAPI-Dependencies.
    """
    with Session(engine) as session:
        yield session
