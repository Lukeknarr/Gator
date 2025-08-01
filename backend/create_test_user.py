#!/usr/bin/env python3
"""
Script to create a test user for development
"""
import os
import sys
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Base
from database import get_engine

def create_test_user():
    """Create a test user for development"""
    try:
        # Get database engine
        engine = get_engine()
        if not engine:
            print("❌ Database engine not available")
            return False
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("✅ Test user already exists")
            return True
        
        # Create password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Create test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=pwd_context.hash("testpass123"),
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("   Username: testuser")
        print("   Password: testpass123")
        print("   Email: test@example.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_test_user() 