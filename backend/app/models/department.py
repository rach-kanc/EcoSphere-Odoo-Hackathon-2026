"""Department ORM model for organizational ownership."""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.csr_activity import CSRActivity
    from app.models.user import User
    from app.models.department_score import DepartmentScore
    from app.models.carbon_transaction import CarbonTransaction


class DeptStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True)
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[DeptStatus] = mapped_column(
        Enum(DeptStatus, name="dept_status"), nullable=False, default=DeptStatus.ACTIVE
    )
    head_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    csr_activities: Mapped[list["CSRActivity"]] = relationship(
        "CSRActivity", back_populates="department"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    scores: Mapped[list["DepartmentScore"]] = relationship(
        "DepartmentScore", back_populates="department"
    )
    carbon_transactions: Mapped[list["CarbonTransaction"]] = relationship(
        "CarbonTransaction", back_populates="department"
    )
    head: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[head_id]
    )
