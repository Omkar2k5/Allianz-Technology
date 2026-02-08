
import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.database.models import User
from app.auth.password import hash_password
import uuid

def create_test_user():
    db = SessionLocal()
    email = "test_sdk@example.com"
    password = "password123"
    
    # Check if exists
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"User {email} already exists.")
        return
        
    hashed_password = hash_password(password)
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hashed_password,
        full_name="Test SDK User",
        is_active=True,
        is_superuser=False
    )
    
    db.add(user)
    db.commit()
    print(f"Created user {email} with password {password}")
    db.close()

if __name__ == "__main__":
    create_test_user()
