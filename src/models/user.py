from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    source_spec: str

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    subscriptions: List[Subscription] = Relationship(back_populates="user")

Subscription.user = Relationship(back_populates="subscriptions", sa_relationship_kwargs={"lazy":"joined"})
