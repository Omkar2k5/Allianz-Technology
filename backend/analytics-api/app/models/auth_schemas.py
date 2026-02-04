"""
Pydantic schemas for authentication endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============================================
# Request Schemas
# ============================================

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    team_name: Optional[str] = Field(None, description="Team name (will create new team if not exists)")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============================================
# Response Schemas
# ============================================

class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    team_id: str
    team_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


class AuthResponse(BaseModel):
    """Schema for authentication response (login/register)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
