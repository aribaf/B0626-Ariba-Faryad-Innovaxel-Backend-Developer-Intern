from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal

from pydantic import BaseModel, Field, validator


class EventBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    total_seats: int = Field(..., gt=0)
    event_date: date

    @validator("name")
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @validator("event_date")
    def event_date_must_be_future(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("event_date must be a future date")
        return value


class EventCreate(EventBase):
    pass


class EventSummary(BaseModel):
    id: int
    name: str
    total_seats: int
    event_date: date
    created_at: datetime
    total_registrations: int
    available_seats: int

    class Config:
        orm_mode = True


class RegistrationBase(BaseModel):
    event_id: int
    user_name: str = Field(..., min_length=1, max_length=255)

    @validator("user_name")
    def normalize_user_name(cls, value: str) -> str:
        return value.strip()


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationRead(BaseModel):
    id: int
    event_id: int
    user_name: str
    status: Literal["active", "cancelled"]
    registered_at: datetime
    cancelled_at: datetime | None = None

    class Config:
        orm_mode = True
