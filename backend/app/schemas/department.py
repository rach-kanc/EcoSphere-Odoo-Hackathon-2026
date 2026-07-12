from pydantic import BaseModel, Field, ConfigDict

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
