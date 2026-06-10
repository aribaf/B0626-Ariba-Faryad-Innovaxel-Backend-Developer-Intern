from __future__ import annotations

from typing import Iterable
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


def get_event_by_name(db: Session, name: str) -> models.Event | None:
    return db.execute(select(models.Event).where(models.Event.name == name)).scalars().first()


def get_event(db: Session, event_id: int) -> models.Event | None:
    return db.execute(select(models.Event).where(models.Event.id == event_id)).scalars().first()


def get_events(db: Session, upcoming_only: bool, sort_ascending: bool) -> list[tuple[models.Event, int]]:
    active_count = (
        select(func.count(models.Registration.id))
        .where(models.Registration.event_id == models.Event.id, models.Registration.status == "active")
        .scalar_subquery()
    )
    query = select(models.Event, active_count.label("active_count"))
    if upcoming_only:
        query = query.where(models.Event.event_date > func.date("now"))
    order_column = models.Event.event_date.asc() if sort_ascending else models.Event.event_date.desc()
    query = query.order_by(order_column)
    return db.execute(query).all()


def create_event(db: Session, event_in: schemas.EventCreate) -> models.Event:
    event = models.Event(
        name=event_in.name,
        total_seats=event_in.total_seats,
        event_date=event_in.event_date,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Event name must be unique") from exc
    db.refresh(event)
    return event


def get_active_registration(db: Session, event_id: int, user_name: str) -> models.Registration | None:
    return (
        db.execute(
            select(models.Registration)
            .where(
                models.Registration.event_id == event_id,
                models.Registration.user_name == user_name,
                models.Registration.status == "active",
            )
        )
        .scalars()
        .first()
    )


def count_active_registrations(db: Session, event_id: int) -> int:
    return db.execute(
        select(func.count(models.Registration.id))
        .where(models.Registration.event_id == event_id, models.Registration.status == "active")
    ).scalar_one()


def count_registrations(db: Session, event_id: int) -> int:
    return db.execute(
        select(func.count(models.Registration.id)).where(models.Registration.event_id == event_id)
    ).scalar_one()


def create_registration(db: Session, registration: models.Registration) -> models.Registration:
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def get_registration(db: Session, registration_id: int) -> models.Registration | None:
    return db.execute(select(models.Registration).where(models.Registration.id == registration_id)).scalars().first()


def get_registrations_for_event(db: Session, event_id: int) -> list[models.Registration]:
    """
    Retrieve active registrations for an event.
    
    Cancelled registrations are excluded from this listing but remain in the database
    for audit/history purposes. This ensures that only currently valid registrations
    are visible to API consumers.
    """
    return db.execute(
        select(models.Registration)
        .where(models.Registration.event_id == event_id, models.Registration.status == "active")
        .order_by(models.Registration.registered_at.asc())
    ).scalars().all()


def get_all_registrations(db: Session, active_only: bool = True) -> list[models.Registration]:
    """
    Retrieve all registrations across all events.
    
    By default returns only active registrations. Set active_only=False to include
    cancelled registrations as well.
    """
    query = select(models.Registration)
    if active_only:
        query = query.where(models.Registration.status == "active")
    return db.execute(query.order_by(models.Registration.registered_at.asc())).scalars().all()


def cancel_registration(db: Session, registration: models.Registration) -> models.Registration:
    registration.status = "cancelled"
    registration.cancelled_at = func.now()
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration
