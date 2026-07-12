"""Department ORM model for organizational ownership."""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    csr_activities: Mapped[list["CSRActivity"]] = relationship(
        "CSRActivity", back_populates="department"
    )
