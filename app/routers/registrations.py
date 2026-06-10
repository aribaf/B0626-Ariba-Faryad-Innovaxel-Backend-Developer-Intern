from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db
from app.services.registration_service import cancel_registration, register_user

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.get("", response_model=List[schemas.RegistrationRead])
def list_all_registrations(
    active_only: bool = Query(True, description="Return only active registrations"),
    db: Session = Depends(get_db),
) -> List[schemas.RegistrationRead]:
    """
    Retrieve all registrations across all events.
    
    By default returns only active registrations. Set active_only=false to include
    cancelled registrations as well for audit purposes.
    """
    return crud.get_all_registrations(db, active_only=active_only)


@router.post("", response_model=schemas.RegistrationRead, status_code=status.HTTP_201_CREATED)
def create_registration(registration_in: schemas.RegistrationCreate, db: Session = Depends(get_db)) -> schemas.RegistrationRead:
    """Create a registration and enforce business constraints."""
    return register_user(db, registration_in)


@router.delete("/{registration_id}", response_model=schemas.RegistrationRead)
def remove_registration(registration_id: int, db: Session = Depends(get_db)) -> schemas.RegistrationRead:
    """Cancel a registration while preserving history."""
    return cancel_registration(db, registration_id)
