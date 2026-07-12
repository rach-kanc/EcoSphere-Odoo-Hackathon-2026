from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ComplianceIssue(Base):
    __tablename__ = "compliance_issues"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    audit_id: Mapped[int | None] = mapped_column(ForeignKey("audits.id", ondelete="SET NULL"), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False) # Low/Medium/High/Critical
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Open") # Open/In Progress/Resolved
    
    # Relationships
    audit = relationship("Audit", back_populates="compliance_issues")
    owner = relationship("User", back_populates="assigned_issues")
