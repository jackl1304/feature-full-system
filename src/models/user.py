# src/models/user.py

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
    Repräsentiert einen Benutzer mit E-Mail und Passwort-Hash.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)  # unique entfernt
    password_hash: str
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Subscription(SQLModel, table=True):
    """
    Verknüpft einen Benutzer mit einem Nachrichten-Plugin.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plugin_name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
