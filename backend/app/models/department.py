"""Department ORM model — organisational hierarchy."""
from __future__ import annotations
from typing import Optional

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeptStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Department(Base):
    """Organisational unit. Supports self-referential parent/child nesting."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    head_id: Mapped[Optional[int ]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    parent_id: Mapped[Optional[int ]] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[DeptStatus] = mapped_column(
        Enum(DeptStatus, name="dept_status"), nullable=False, default=DeptStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="department", foreign_keys="User.department_id")  # type: ignore[name-defined]
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent", foreign_keys=[parent_id])
    parent: Mapped[Optional["Department "]] = relationship("Department", back_populates="children", remote_side="Department.id", foreign_keys=[parent_id])
    carbon_transactions: Mapped[list["CarbonTransaction"]] = relationship("CarbonTransaction", back_populates="department")  # type: ignore[name-defined]
    scores: Mapped[list["DepartmentScore"]] = relationship("DepartmentScore", back_populates="department")  # type: ignore[name-defined]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Department {self.code} — {self.name}>"
