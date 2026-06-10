from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import crud, models, schemas


def register_user(db: Session, registration_in: schemas.RegistrationCreate) -> models.Registration:
    """Register a user for an event, enforcing availability and duplicate rules."""
    if db.bind and db.bind.dialect.name == "sqlite":
        db.execute(text("BEGIN IMMEDIATE"))

    event = crud.get_event(db, registration_in.event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.event_date <= date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot register for past or same-day events")

    existing_registration = crud.get_active_registration(db, registration_in.event_id, registration_in.user_name)
    if existing_registration is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active registration for this event",
        )

    current_active = crud.count_active_registrations(db, registration_in.event_id)
    if current_active >= event.total_seats:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is full")

    registration = models.Registration(
        event_id=registration_in.event_id,
        user_name=registration_in.user_name,
        status="active",
        registered_at=datetime.utcnow(),
    )
    try:
        db.add(registration)
        db.commit()
        db.refresh(registration)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create registration") from exc

    return registration


def cancel_registration(db: Session, registration_id: int) -> models.Registration:
    """Cancel an existing registration by ID."""
    registration = crud.get_registration(db, registration_id)
    if registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")

    if registration.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration is already cancelled")

    registration.status = "cancelled"
    registration.cancelled_at = datetime.utcnow()
    try:
        db.add(registration)
        db.commit()
        db.refresh(registration)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel registration") from exc

    return registration
