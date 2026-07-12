"""Department ORM model.

Minimal organisational unit used as the FK target for carbon transactions and,
later, ESG scoring. This is a stub covering only what dependent models need;
the full Department (hierarchy, manager, etc.) is owned by the Phase 1 work.
"""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Department {self.name}>"
