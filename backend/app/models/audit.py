from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Audit(Base):
    __tablename__ = "audits"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    auditor: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    findings_summary: Mapped[str | None] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="Scheduled") # Scheduled/In Progress/Completed
    
    # Relationships
    department = relationship("Department", back_populates="audits")
    compliance_issues = relationship("ComplianceIssue", back_populates="audit", cascade="all, delete-orphan")
