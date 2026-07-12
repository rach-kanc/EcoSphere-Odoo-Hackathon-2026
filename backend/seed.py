"""Seed helper for default master data."""
from __future__ import annotations

from app.core.database import SessionLocal
from app.services.category_service import CategoryService


def seed_categories() -> None:
    db = SessionLocal()
    try:
        service = CategoryService(db)
        service.seed_default_csr_categories(
            ["Environment", "Education", "Health", "Community"]
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()
