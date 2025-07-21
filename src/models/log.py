from datetime import datetime
from sqlmodel import SQLModel, Field

class FetchLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_spec: str
    status: str       # "success" oder "error"
    details: str      # Fehlermeldung oder Anzahl der Artikel
