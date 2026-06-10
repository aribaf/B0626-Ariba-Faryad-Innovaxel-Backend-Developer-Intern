from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.routers import events, registrations

app = FastAPI(
    title="Event Registration API",
    description="A backend service for event creation and user registrations with seat management.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()


app.include_router(events.router)
app.include_router(registrations.router)
