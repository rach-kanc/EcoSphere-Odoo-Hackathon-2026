from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    points_balance: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    acknowledgements = relationship("PolicyAcknowledgement", back_populates="employee", cascade="all, delete-orphan")
    assigned_issues = relationship("ComplianceIssue", back_populates="owner", cascade="all, delete-orphan")
