from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ComplianceIssueBase(BaseModel):
    audit_id: int | None = None
    severity: str = Field(..., max_length=50) # Low/Medium/High/Critical
    description: str
    owner_id: int
    due_date: datetime
    status: str = Field("Open", max_length=50) # Open/In Progress/Resolved

class ComplianceIssueCreate(BaseModel):
    audit_id: int | None = None
    severity: str = Field(..., max_length=50)
    description: str
    owner_id: int = Field(..., description="Owner ID is mandatory")
    due_date: datetime = Field(..., description="Due date is mandatory")

class ComplianceIssueUpdate(BaseModel):
    audit_id: int | None = None
    severity: str | None = Field(None, max_length=50)
    description: str | None = None
    owner_id: int | None = None
    due_date: datetime | None = None
    status: str | None = Field(None, max_length=50)

class ComplianceIssueRead(ComplianceIssueBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
