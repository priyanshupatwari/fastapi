from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr   # Validates that the string is a properly formatted email


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
