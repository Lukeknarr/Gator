#!/usr/bin/env python3
"""
Initialize Railway PostgreSQL database with tables
"""
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Import models to create tables
from models import Base

load_dotenv()

def init_database():
    """Initialize the database with tables"""
    print("🔧 Initializing Railway PostgreSQL database...")
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"📡 Database URL: {database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List created tables
        with engine.connect() as connection:
            result = connection.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database() 