from pydantic import BaseModel, EmailStr
from typing import Optional

# Shared properties
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Properties for user creation
class UserCreate(UserBase):
    password: str  # raw password, will be hashed before storing
    role: str | None = None

# Properties for returning user info in responses
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
