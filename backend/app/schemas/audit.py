from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AuditBase(BaseModel):
    title: str = Field(..., max_length=255)
    department_id: int
    auditor: str = Field(..., max_length=255)
    date: datetime
    findings_summary: str | None = ""
    status: str = Field("Scheduled", max_length=50) # Scheduled/In Progress/Completed

class AuditCreate(AuditBase):
    pass

class AuditUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    department_id: int | None = None
    auditor: str | None = Field(None, max_length=255)
    date: datetime | None = None
    findings_summary: str | None = None
    status: str | None = Field(None, max_length=50)

class AuditRead(AuditBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
