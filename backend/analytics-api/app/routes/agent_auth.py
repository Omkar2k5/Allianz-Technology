"""
Agent-specific authentication endpoints
Simplified auth for desktop agent with minimal response payload
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import uuid

from app.database.connection import get_db
from app.database.models import User, Team, RefreshToken
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token

router = APIRouter()

class AgentLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AgentRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class AgentAuthResponse(BaseModel):
    user_id: str
    email: str
    jwt_token: str
    refresh_token: str | None = None
    expires_in: int  # seconds

@router.post("/login", response_model=AgentAuthResponse)
async def agent_login(credentials: AgentLoginRequest, db: Session = Depends(get_db)):
    """
    Simplified login endpoint for desktop agent
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    # user.last_login = datetime.utcnow()
    # db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token_str = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(refresh_token)
    db.commit()
    
    # Calculate expires_in (7 days in seconds)
    expires_in = 60 * 60 * 24 * 7
    
    return AgentAuthResponse(
        user_id=str(user.id),
        email=user.email,
        jwt_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=expires_in
    )

@router.post("/register", response_model=AgentAuthResponse, status_code=status.HTTP_201_CREATED)
async def agent_register(user_data: AgentRegisterRequest, db: Session = Depends(get_db)):
    """
    Simplified registration endpoint for desktop agent
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create a personal team
    team = Team(
        id=uuid.uuid4(),
        name=f"{user_data.name}'s Team",
        organization=f"{user_data.name}'s Organization",
        subscription_tier='free'
    )
    db.add(team)
    db.flush()
    
    # Hash password
    password_hashed = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        id=uuid.uuid4(),
        # team_id=team.id, # User model doesn't support teams yet
        email=user_data.email,
        hashed_password=password_hashed,
        full_name=user_data.name,
        # first_name=first_name,
        # last_name=last_name,
        # role='viewer',
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    refresh_token_str = create_refresh_token(data={"sub": str(new_user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=new_user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(refresh_token)
    db.commit()
    
    # Calculate expires_in (7 days in seconds)
    expires_in = 60 * 60 * 24 * 7
    
    return AgentAuthResponse(
        user_id=str(new_user.id),
        email=new_user.email,
        jwt_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=expires_in
    )
