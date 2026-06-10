# Event Registration API

A simple backend service for creating events, registering users, and managing seat availability using FastAPI, SQLAlchemy, and SQLite.

## Features

- Create events with unique names, future dates, and valid seat counts
- Register users to events with active registration enforcement
- Prevent duplicate registrations for the same user and event
- Prevent overbooking through transactional registration logic
- Cancel registrations without deleting data
- Query events with optional upcoming filtering and date sorting
- View registrations for a specific event

## Project Structure

```
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── dependencies.py
├── routers/
│   ├── events.py
│   └── registrations.py
└── services/
    └── registration_service.py
requirements.txt
README.md
.gitignore
```

## Setup

1. Create a Python 3.11+ virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Start the API server

```bash
uvicorn app.main:app --reload
```

4. Open API docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Create Event

- `POST /events`
- Request body:
  ```json
  {
    "name": "Annual Conference",
    "total_seats": 150,
    "event_date": "2026-08-10"
  }
  ```
- Response:
  ```json
  {
    "id": 1,
    "name": "Annual Conference",
    "total_seats": 150,
    "event_date": "2026-08-10",
    "created_at": "2026-06-10T12:00:00.000000",
    "total_registrations": 0,
    "available_seats": 150
  }
  ```

### List Events

- `GET /events`
- Query params:
  - `upcoming` (boolean)
  - `sort_ascending` (boolean)
- Response returns events with registration counts and availability.

### Get Event Details

- `GET /events/{id}`
- Response includes available seats and total registrations.

### Register User

- `POST /registrations`
- Request body:
  ```json
  {
    "event_id": 1,
    "user_name": "Jane Doe"
  }
  ```
- Response:
  ```json
  {
    "id": 1,
    "event_id": 1,
    "user_name": "Jane Doe",
    "status": "active",
    "registered_at": "2026-06-10T12:10:00.000000",
    "cancelled_at": null
  }
  ```

### Cancel Registration

- `DELETE /registrations/{id}`
- Response returns the cancelled registration record.

### Get Event Registrations

- `GET /events/{id}/registrations`
- Returns **active registrations only** for the event
- Cancelled registrations are excluded from this list (see note below)
- Response includes all currently valid user registrations

## Design Decisions

- `Event` and `Registration` share a one-to-many relationship with SQLAlchemy ORM.
- Registration cancellation preserves history by updating `status` and `cancelled_at`.
- Active seat count is calculated dynamically so cancelled registrations do not consume seats.
- SQLite transactions use `BEGIN IMMEDIATE` to reduce overbooking risks under concurrency.
- Input validation is enforced by Pydantic models and domain checks in service logic.
- **Cancelled registrations are excluded from active registration listings** but remain in the database for audit purposes. The `GET /events/{id}/registrations` endpoint returns only registrations with `status="active"`.

## Assumptions

- `total_registrations` reflects active registrations for the purposes of seat availability.
- Cancelled registrations are retained for auditing, but they do not count toward active registrations or occupied seats.
- Event dates are compared against the current date in the server timezone.
- The `GET /events/{id}/registrations` endpoint returns only active registrations. Cancelled registrations remain in the database but are excluded from this listing.

## Running Locally

```bash
uvicorn app.main:app --reload
```

## Notes

- The database file is created automatically as `app.db` in the project root.
- Use the auto-generated OpenAPI docs to experiment with the API.
