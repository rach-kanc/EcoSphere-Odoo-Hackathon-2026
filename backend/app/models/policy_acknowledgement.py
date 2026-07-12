from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class PolicyAcknowledgement(Base):
    __tablename__ = "policy_acknowledgements"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("esg_policies.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Pending") # Pending/Acknowledged
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    policy = relationship("ESGPolicy", back_populates="acknowledgements")
    employee = relationship("User", back_populates="acknowledgements")
    
    __table_args__ = (
        UniqueConstraint("policy_id", "employee_id", name="uq_policy_employee"),
    )
