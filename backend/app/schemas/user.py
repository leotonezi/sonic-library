from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MeResponse(UserResponse):
    is_admin: bool

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None