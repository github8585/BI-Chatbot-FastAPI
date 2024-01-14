from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


# Base Schema
class UserBase(BaseModel):
    username: str
    secret: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Creation Schema
class UserIn(UserBase):
    secret: str  # Assuming 'secret' is used like a password

# Response Schema
class UserResponse(UserBase):
    pass  # You can add additional fields here if needed for responses

# Database Schema
class UserInDBBase(UserBase):
    id: int  # Assuming there's an ID field in your database model

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str

