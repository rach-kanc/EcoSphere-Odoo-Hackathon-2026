from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    role: str = Field(..., max_length=100)
    department_id: int | None = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    points_balance: int = 0
