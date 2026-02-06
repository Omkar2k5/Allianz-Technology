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

def get_name_parts(full_name: str):
    parts = (full_name or "").split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hashed = hash_password(user_data.password)
    
    # Create user
    # Note: Current User model uses full_name and does not have team_id
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        hashed_password=password_hashed,
        full_name=f"{user_data.first_name} {user_data.last_name}".strip(),
        # role='viewer', # User model might not have role, check schema. Assuming removed or defaulted.
        is_active=True
    )
    
    # If the User model has 'role', set it. The provided dump didn't show it explicitly but models.py scan had it?
    # Re-checking models.py scan: "role" was NOT in the User class provided in previous turn!
    # "is_superuser" was there.
    # So I removed 'role'.
    
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
    
    first, last = get_name_parts(new_user.full_name)

    # Prepare user response
    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        role="admin" if new_user.is_superuser else "viewer",
        first_name=first,
        last_name=last,
        team_id=None,
        team_name=None,
        is_active=new_user.is_active,
        # last_login=new_user.last_login, # Check fields
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
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
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
    
    # Update last login (field does not exist in User model)
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
    
    first, last = get_name_parts(user.full_name)
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=first,
        last_name=last,
        role="viewer",
        team_id=None,
        team_name=None,
        is_active=user.is_active,
        # last_login=user.last_login,
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
    
    first, last = get_name_parts(user.full_name)
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=first,
        last_name=last,
        role="viewer",
        team_id=None,
        team_name=None,
        is_active=user.is_active,
        # last_login=user.last_login,
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
    """
    first, last = get_name_parts(current_user.full_name)
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=first,
        last_name=last,
        role="viewer",
        team_id=None,
        team_name=None,
        is_active=current_user.is_active,
        # last_login=current_user.last_login,
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
    """
    # Update fields if provided
    first, last = get_name_parts(current_user.full_name)
    new_first = user_update.first_name if user_update.first_name is not None else first
    new_last = user_update.last_name if user_update.last_name is not None else last
    
    if user_update.first_name is not None or user_update.last_name is not None:
        current_user.full_name = f"{new_first} {new_last}".strip()
    
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
    
    first, last = get_name_parts(current_user.full_name)
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=first,
        last_name=last,
        role="viewer",
        team_id=None,
        team_name=None,
        is_active=current_user.is_active,
        # last_login=current_user.last_login,
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
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = hash_password(password_data.new_password)
    
    # Update password
    current_user.hashed_password = new_password_hash
    db.commit()
    
    return MessageResponse(message="Password changed successfully")

