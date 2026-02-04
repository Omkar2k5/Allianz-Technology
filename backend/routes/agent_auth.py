from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import bcrypt
import uuid
from typing import Optional

from ..database.connection import get_db
from ..models import User

router = APIRouter(prefix="/api/agent", tags=["agent-auth"])

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class AuthResponse(BaseModel):
    user_id: str
    email: str
    jwt_token: str
    refresh_token: Optional[str] = None
    expires_in: int  # seconds

def create_access_token(user_id: str, email: str) -> tuple[str, int]:
    """Create JWT access token"""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, int(expires_delta.total_seconds())

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Agent login endpoint"""
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    jwt_token, expires_in = create_access_token(str(user.id), user.email)
    
    return AuthResponse(
        user_id=str(user.id),
        email=user.email,
        jwt_token=jwt_token,
        expires_in=expires_in
    )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Agent registration endpoint"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        email=request.email,
        name=request.name,
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    jwt_token, expires_in = create_access_token(str(new_user.id), new_user.email)
    
    return AuthResponse(
        user_id=str(new_user.id),
        email=new_user.email,
        jwt_token=jwt_token,
        expires_in=expires_in
    )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh JWT token (placeholder for now)"""
    # TODO: Implement refresh token logic
    raise HTTPException(status_code=501, detail="Refresh token not implemented yet")
