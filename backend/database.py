from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ CRITICAL ERROR: DATABASE_URL environment variable is not set!")
    print("🔍 Available environment variables:")
    for key, value in os.environ.items():
        if "DATABASE" in key or "POSTGRES" in key or "DB" in key:
            print(f"  {key}: {value}")
    raise RuntimeError("DATABASE_URL environment variable is required but not set")

POSTGRES_URL = DATABASE_URL
print(f"✅ DATABASE_URL found: {DATABASE_URL[:50]}...")
engine = None
SessionLocal = None
Base = declarative_base()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
neo4j_driver = None

def get_engine():
    """Lazy initialization of PostgreSQL engine"""
    global engine
    if engine is None:
        try:
            engine = create_engine(POSTGRES_URL)
        except Exception as e:
            print(f"Warning: Could not create PostgreSQL engine: {e}")
            return None
    return engine

def get_session_local():
    """Lazy initialization of session maker"""
    global SessionLocal
    if SessionLocal is None:
        engine = get_engine()
        if engine:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

def get_neo4j_driver():
    """Lazy initialization of Neo4j driver"""
    global neo4j_driver
    if neo4j_driver is None:
        try:
            neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        except Exception as e:
            print(f"Warning: Could not create Neo4j driver: {e}")
            return None
    return neo4j_driver

def get_db():
    """Get database session with error handling"""
    try:
        SessionLocal = get_session_local()
        if SessionLocal:
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        else:
            yield None
    except Exception as e:
        print(f"Database connection error: {e}")
        yield None

def get_neo4j_session():
    """Get Neo4j session with error handling"""
    try:
        driver = get_neo4j_driver()
        if driver:
            with driver.session() as session:
                yield session 
        else:
            yield None
    except Exception as e:
        print(f"Neo4j connection error: {e}")
        yield None 