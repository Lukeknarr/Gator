#!/usr/bin/env python3
"""
Database initialization script for Gator production deployment.
Run this script to set up the database schema and initial data.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, User, Tag
from database import engine

load_dotenv()

async def init_database():
    """Initialize the database with schema and initial data."""
    print("🚀 Initializing Gator database...")
    
    try:
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if initial data already exists
        existing_users = db.query(User).count()
        existing_tags = db.query(Tag).count()
        
        if existing_users == 0:
            print("👥 Creating initial users...")
            # Create admin user
            admin_user = User(
                email="admin@gator.com",
                username="admin",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUyGm",  # admin123
                is_active=True
            )
            db.add(admin_user)
            print("✅ Admin user created")
        
        if existing_tags == 0:
            print("🏷️ Creating initial tags...")
            initial_tags = [
                {"name": "technology", "category": "topic"},
                {"name": "politics", "category": "topic"},
                {"name": "science", "category": "topic"},
                {"name": "business", "category": "topic"},
                {"name": "health", "category": "topic"},
                {"name": "artificial intelligence", "category": "domain"},
                {"name": "machine learning", "category": "domain"},
                {"name": "data science", "category": "domain"},
                {"name": "startups", "category": "domain"},
                {"name": "climate change", "category": "topic"},
                {"name": "finance", "category": "topic"},
                {"name": "education", "category": "topic"},
                {"name": "environment", "category": "topic"},
                {"name": "psychology", "category": "topic"},
                {"name": "philosophy", "category": "topic"},
                {"name": "history", "category": "topic"},
                {"name": "art", "category": "topic"},
                {"name": "music", "category": "topic"},
                {"name": "sports", "category": "topic"},
                {"name": "travel", "category": "topic"},
                {"name": "cooking", "category": "topic"}
            ]
            
            for tag_data in initial_tags:
                tag = Tag(**tag_data)
                db.add(tag)
            
            print(f"✅ {len(initial_tags)} initial tags created")
        
        # Commit changes
        db.commit()
        db.close()
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_database()) 