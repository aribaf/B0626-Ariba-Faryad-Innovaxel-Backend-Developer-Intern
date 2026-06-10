# Event Registration API

A simple backend service for creating events, registering users, and managing seat availability using FastAPI, SQLAlchemy, and SQLite.

## Overview

This project implements an Event Registration System API that allows users to: 

* Create events with limited seat capacity
* Register users for events
* Prevent duplicate registrations
* Prevent overbooking
* Cancel registrations while preserving history
* View events with registration statistics
* Filter and sort events

The API is built using FastAPI, SQLAlchemy ORM, and SQLite.

---

## Features

* Create events with unique names
* Validate future event dates
* Validate positive seat counts
* Register users for events
* Prevent duplicate registrations
* Prevent registrations when an event is full
* Store registration timestamps
* Cancel registrations without deleting historical data
* View active registrations for an event
* Filter upcoming events
* Sort events by date
* Automatic OpenAPI/Swagger documentation
* Persistent SQLite storage

---

## Project Structure

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── dependencies.py
│
├── routers/
│   ├── events.py
│   └── registrations.py
│
└── services/
    └── registration_service.py

requirements.txt
README.md
.gitignore
```

---

## Technology Stack

* Python 3.11+
* FastAPI
* SQLAlchemy ORM
* SQLite
* Pydantic
* Uvicorn

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

### 4. Open API documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## API Endpoints

### Events

#### Create Event

```http
POST /events
```

Example Request:

```json
{
  "name": "Annual Conference",
  "total_seats": 150,
  "event_date": "2026-08-10"
}
```

---

#### List Events

```http
GET /events
```

Query Parameters:

| Parameter      | Type    | Description               |
| -------------- | ------- | ------------------------- |
| upcoming       | boolean | Return only future events |
| sort_ascending | boolean | Sort events by date       |

Returns:

* Total registrations
* Available seats
* Event details

---

#### Get Event Details

```http
GET /events/{event_id}
```

Returns:

* Event information
* Total registrations
* Available seats

---

#### Get Event Registrations

```http
GET /events/{event_id}/registrations
```

Returns only **active registrations**.

Cancelled registrations remain stored in the database for audit/history purposes but are excluded from this endpoint.

---

### Registrations

#### Register User

```http
POST /registrations
```

Example Request:

```json
{
  "event_id": 1,
  "user_name": "Jane Doe"
}
```

---

#### Cancel Registration

```http
DELETE /registrations/{registration_id}
```

Cancels a registration while preserving historical records.

---

## Design Decisions

### Event and Registration Relationship

An Event can have many Registrations.

A Registration belongs to one Event.

### Soft Cancellation

Registrations are not deleted.

Instead:

* status = "cancelled"
* cancelled_at timestamp is stored

This preserves registration history.

### Seat Availability

Available seats are calculated dynamically:

```text
available_seats = total_seats - active_registrations
```

This prevents inconsistencies caused by storing seat counts separately.

### Active Registrations

Only registrations with:

```text
status = "active"
```

are counted toward:

* Total registrations
* Available seat calculations
* Registration listings

### Overbooking Protection

SQLite transactions use:

```sql
BEGIN IMMEDIATE
```

before registration checks to reduce race conditions and overbooking when multiple users attempt to register simultaneously.

### Validation

Validation is enforced using Pydantic and business rules:

* Event name must be unique
* Event date must be in the future
* Total seats must be greater than zero
* Duplicate registrations are not allowed
* Full events reject new registrations

---

## Assumptions

* Event dates are compared using the server's current date.
* Cancelled registrations remain in the database.
* Only active registrations consume seats.
* total_registrations represents active registrations.

---

## Testing

The API was manually tested through FastAPI Swagger UI.

### Tested Scenarios

* Event creation
* Duplicate event name validation
* Future date validation
* Invalid seat count validation
* Event retrieval
* Event filtering
* Event sorting
* User registration
* Duplicate registration prevention
* Full event prevention
* Registration cancellation
* Seat availability recalculation
* Active registration filtering
* Invalid event IDs
* Invalid registration IDs

---

## Running Locally

```bash
uvicorn app.main:app --reload
```

---

## Notes

* The SQLite database file (`app.db`) is generated automatically.
* FastAPI automatically generates interactive API documentation.
* The project focuses on the Event Registration System requirements described in the assessment.
