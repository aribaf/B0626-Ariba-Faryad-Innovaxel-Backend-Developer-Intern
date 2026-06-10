from __future__ import annotations

from typing import Iterator
from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Iterator[Session]:
    """Provide a database session for request handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
