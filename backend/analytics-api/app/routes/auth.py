"""
Authentication endpoints for user registration, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.database.connection import get_db
from app.database.models import User, Team, RefreshToken
from app.models.auth_schemas import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserUpdate,
    PasswordChange,
    UserResponse,
    AuthResponse,
    MessageResponse
)
from app.auth.password import hash_password, verify_password
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user
)


router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - Creates a new user account
    - Optionally creates a new team if team_name is provided
    - Returns access and refresh tokens
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get or create team
    if user_data.team_name:
        team = db.query(Team).filter(Team.name == user_data.team_name).first()
        if not team:
            # Create new team
            team = Team(
                id=uuid.uuid4(),
                name=user_data.team_name,
                organization=user_data.team_name,
                subscription_tier='free'
            )
            db.add(team)
            db.flush()
    else:
        # Create a personal team
        team = Team(
            id=uuid.uuid4(),
            name=f"{user_data.first_name}'s Team",
            organization=f"{user_data.first_name}'s Organization",
            subscription_tier='free'
        )
        db.add(team)
        db.flush()
    
    # Hash password
    password_hashed = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        id=uuid.uuid4(),
        team_id=team.id,
        email=user_data.email,
        password_hash=password_hashed,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role='viewer',  # Default role
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
    
    # Prepare user response
    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        team_id=str(new_user.team_id),
        team_name=team.name,
        is_active=new_user.is_active,
        last_login=new_user.last_login,
        created_at=new_user.created_at
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        user=user_response
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    - Validates credentials
    - Returns access and refresh tokens
    - Updates last_login timestamp
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
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
    
    # Get team info
    team = db.query(Team).filter(Team.id == user.team_id).first()
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        team_id=str(user.team_id),
        team_name=team.name if team else None,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        user=user_response
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Returns new access and refresh tokens
    """
    # Verify refresh token
    try:
        payload = verify_token(token_data.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token exists in database
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # Check if token is expired
    if stored_token.expires_at < datetime.utcnow():
        db.delete(stored_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == stored_token.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Delete old refresh token
    db.delete(stored_token)
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store new refresh token
    refresh_token_obj = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(refresh_token_obj)
    db.commit()
    
    # Get team info
    team = db.query(Team).filter(Team.id == user.team_id).first()
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        team_id=str(user.team_id),
        team_name=team.name if team else None,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    token_data: TokenRefresh,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating refresh token
    
    - Deletes refresh token from database
    - Client should also delete access token
    """
    # Delete refresh token
    db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).delete()
    db.commit()
    
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user's information
    
    - Returns user profile data
    - Requires valid access token
    """
    # Get team info
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        team_id=str(current_user.team_id),
        team_name=team.name if team else None,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    
    - Updates first_name, last_name, or email
    - Requires valid access token
    """
    # Update fields if provided
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    # Get team info
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        team_id=str(current_user.team_id),
        team_name=team.name if team else None,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )


@router.put("/password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    - Requires current password verification
    - Updates to new password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = hash_password(password_data.new_password)
    
    # Update password
    current_user.password_hash = new_password_hash
    db.commit()
    
    return MessageResponse(message="Password changed successfully")
