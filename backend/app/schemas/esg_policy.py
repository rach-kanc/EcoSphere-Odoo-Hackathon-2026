from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ESGPolicyBase(BaseModel):
    title: str = Field(..., max_length=255)
    category: str = Field(..., max_length=50) # Environmental/Social/Governance
    content: str
    version: str = Field("1.0", max_length=20)
    status: str = Field("Draft", max_length=50) # Draft/Published/Archived

class ESGPolicyCreate(ESGPolicyBase):
    pass

class ESGPolicyUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    category: str | None = Field(None, max_length=50)
    content: str | None = None
    version: str | None = Field(None, max_length=20)
    status: str | None = Field(None, max_length=50)
    published_at: datetime | None = None

class ESGPolicyRead(ESGPolicyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    published_at: datetime | None = None
