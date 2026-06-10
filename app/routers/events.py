from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/events", tags=["events"])


def build_event_summary(event: models.Event, active_count: int) -> schemas.EventSummary:
    return schemas.EventSummary(
        id=event.id,
        name=event.name,
        total_seats=event.total_seats,
        event_date=event.event_date,
        created_at=event.created_at,
        total_registrations=active_count,
        available_seats=max(event.total_seats - active_count, 0),
    )


@router.post("", response_model=schemas.EventSummary, status_code=status.HTTP_201_CREATED)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)) -> schemas.EventSummary:
    """Create a new event with unique name and future date."""
    try:
        created_event = crud.create_event(db, event_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    active_count = crud.count_active_registrations(db, created_event.id)
    return build_event_summary(created_event, active_count)


@router.get("", response_model=List[schemas.EventSummary])
def list_events(
    upcoming: bool = Query(False, description="Return only events with a future date"),
    sort_ascending: bool = Query(True, description="Sort events by date ascending"),
    db: Session = Depends(get_db),
) -> List[schemas.EventSummary]:
    """Retrieve all events, optionally filtering to only upcoming events."""
    rows = crud.get_events(db, upcoming_only=upcoming, sort_ascending=sort_ascending)
    return [build_event_summary(event, active_count) for event, active_count in rows]


@router.get("/{event_id}", response_model=schemas.EventSummary)
def get_event_details(event_id: int, db: Session = Depends(get_db)) -> schemas.EventSummary:
    """Get detailed information for a single event."""
    event = crud.get_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    active_count = crud.count_active_registrations(db, event_id)
    return build_event_summary(event, active_count)


@router.get("/{event_id}/registrations", response_model=List[schemas.RegistrationRead])
def get_event_registrations(event_id: int, db: Session = Depends(get_db)) -> List[schemas.RegistrationRead]:
    """
    Return active registrations for a specified event.
    
    Only returns registrations with status="active". Cancelled registrations are
    excluded from this endpoint but remain stored in the database for audit purposes.
    """
    event = crud.get_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return crud.get_registrations_for_event(db, event_id)
