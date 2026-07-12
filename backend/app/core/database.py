"""Database engine, session factory, and declarative Base.

SQLite is used for local development; set DATABASE_URL to a PostgreSQL DSN in
production (see .env.example). All ORM models inherit from ``Base``.
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecosphere.db")

# ``check_same_thread`` is only needed for SQLite; harmless to omit elsewhere.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def get_db():
    """FastAPI dependency that yields a scoped session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
