from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PolicyAcknowledgementBase(BaseModel):
    policy_id: int
    employee_id: int
    status: str = Field("Pending", max_length=50) # Pending/Acknowledged

class PolicyAcknowledgementCreate(BaseModel):
    policy_id: int
    employee_id: int

class PolicyAcknowledgementUpdate(BaseModel):
    status: str = Field(..., max_length=50)

class PolicyAcknowledgementRead(PolicyAcknowledgementBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    acknowledged_at: datetime | None = None
