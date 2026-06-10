from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    total_seats = Column(Integer, nullable=False)
    event_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    registrations = relationship(
        "Registration",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_name = Column(String(255), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active")
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="registrations")
