#!/usr/bin/env python3
"""
Test database connection script
"""
import os
import sys
from sqlalchemy import create_engine
from neo4j import GraphDatabase

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        postgres_url = os.getenv("POSTGRES_URL")
        print(f"Testing PostgreSQL connection...")
        print(f"URL: {postgres_url}")
        
        engine = create_engine(postgres_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ PostgreSQL connection successful!")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_neo4j_connection():
    """Test Neo4j connection"""
    try:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        print(f"Testing Neo4j connection...")
        print(f"URI: {neo4j_uri}")
        print(f"User: {neo4j_user}")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            result = session.run("RETURN 1")
            print("✅ Neo4j connection successful!")
            return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def main():
    """Test all database connections"""
    print("🔍 Testing database connections...")
    print("=" * 50)
    
    # Test PostgreSQL
    postgres_ok = test_postgres_connection()
    print()
    
    # Test Neo4j
    neo4j_ok = test_neo4j_connection()
    print()
    
    if postgres_ok and neo4j_ok:
        print("✅ All database connections successful!")
    else:
        print("❌ Some database connections failed!")
        print("\nTroubleshooting tips:")
        print("1. Check if the database URLs are correct")
        print("2. Verify the database credentials")
        print("3. Ensure the databases are accessible from Railway")

if __name__ == "__main__":
    main() 