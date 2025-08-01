from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from database import get_db, engine
from models import Base, User, UserInterest, Content, UserInteraction
from schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    InterestCreate, InterestResponse, ContentResponse,
    RecommendationRequest, RecommendationResponse,
    UserOnboarding, FeedbackRequest
)
from services.auth_service import AuthService
from services.interest_service import InterestService
from services.recommendation_service import RecommendationService
from services.content_service import ContentService
from services.summarization_service import AISummarizationService
from services.premium_service import PremiumService
from services.connection_map_service import connection_map_service

app = FastAPI(
    title="Gator AI",
    description="Personalized media discovery engine",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    print("🚀 Gator backend starting up...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Port: {os.getenv('PORT', '8000')}")
    
    try:
        engine = get_engine()
        if engine:
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully")
        else:
            print("⚠️  Warning: Database not available, skipping table creation")
    except Exception as e:
        print(f"⚠️  Warning: Could not create database tables: {e}")
    
    print("✅ Gator backend startup complete!")

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Services
auth_service = AuthService(pwd_context)
interest_service = InterestService()
recommendation_service = RecommendationService()
content_service = ContentService()
summarization_service = AISummarizationService()
premium_service = PremiumService()

@app.get("/")
async def root():
    """Simple root endpoint for basic health checks"""
    return {"message": "Gator API - Personalized Media Discovery Engine", "status": "running", "health": "ok"}

@app.get("/health")
async def health_check():
    """Simple health check that doesn't depend on database"""
    return {"status": "healthy", "message": "Gator backend is live!", "timestamp": "2024-07-31T23:57:00Z"}

@app.get("/healthcheck")
async def railway_healthcheck():
    """Dedicated healthcheck endpoint for Railway"""
    return {"status": "ok", "service": "gator-backend"}

@app.get("/health/db")
async def database_health_check():
    """Check database connectivity"""
    try:
        engine = get_engine()
        if engine:
            # Test PostgreSQL connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "not_available"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "error": str(e)}

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return auth_service.register_user(db, user)

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    return auth_service.login_user(db, form_data.username, form_data.password)

@app.post("/onboarding", response_model=UserResponse)
async def user_onboarding(
    onboarding_data: UserOnboarding,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Complete user onboarding with initial interests"""
    return interest_service.complete_onboarding(db, current_user, onboarding_data)

@app.get("/interests", response_model=List[InterestResponse])
async def get_user_interests(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interest graph"""
    return interest_service.get_user_interests(db, current_user.id)

@app.post("/interests", response_model=InterestResponse)
async def add_interest(
    interest: InterestCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new interest to user's graph"""
    return interest_service.add_interest(db, current_user.id, interest)

@app.get("/recommendations", response_model=List[ContentResponse])
async def get_recommendations(
    limit: int = 20,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for user"""
    return recommendation_service.get_recommendations(db, current_user.id, limit)

@app.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Submit user feedback on content"""
    return recommendation_service.submit_feedback(db, current_user.id, feedback)

@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get specific content details"""
    return content_service.get_content(db, content_id)

@app.get("/content/search")
async def search_content(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search content across all sources"""
    return content_service.search_content(db, query, limit)

@app.get("/user/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get current user profile"""
    return current_user

@app.post("/user/export")
async def export_user_data(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Export user data in JSON format"""
    return interest_service.export_user_data(db, current_user.id)

# Passive tracking endpoints
@app.post("/passive-tracking")
async def track_page_visit(
    tracking_data: dict,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Track user's passive page visits"""
    return {"message": "Tracking data received", "user_id": current_user.id}

@app.post("/passive-tracking/batch")
async def track_page_visits_batch(
    tracking_data: dict,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Track multiple page visits"""
    return {"message": "Batch tracking data received", "user_id": current_user.id}

# AI Summarization endpoints
@app.post("/content/{content_id}/summarize")
async def summarize_content(
    content_id: int,
    summary_type: str = "hybrid",
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI summary for content"""
    content = content_service.get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return summarization_service.summarize_content(content, summary_type)

@app.get("/content/{content_id}/summary")
async def get_content_summary(
    content_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get existing summary for content"""
    return summarization_service.get_summary_for_content(content_id)

# Cross-interest connection endpoints
@app.get("/connections/novel")
async def get_novel_connections(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get novel connections between user interests"""
    user_interests = interest_service.get_user_interests(db, current_user.id)
    content_data = content_service.get_all_content(db)
    
    return connection_map_service.find_novel_connections(user_interests, content_data)

@app.get("/connections/exploration")
async def get_exploration_paths(
    exploration_level: str = "moderate",
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get exploration paths for user"""
    user_interests = interest_service.get_user_interests(db, current_user.id)
    content_data = content_service.get_all_content(db)
    
    return connection_map_service.suggest_exploration_paths(user_interests, content_data, exploration_level)

# Premium endpoints
@app.get("/premium/status")
async def check_premium_status(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Check user's premium status"""
    return {"is_premium": premium_service.check_premium_access(current_user.id)}

@app.get("/premium/recommendations")
async def get_premium_recommendations(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get premium recommendations"""
    if not premium_service.check_premium_access(current_user.id):
        raise HTTPException(status_code=403, detail="Premium access required")
    
    user_interests = interest_service.get_user_interests(db, current_user.id)
    return premium_service.get_premium_recommendations(current_user.id, user_interests)

@app.get("/premium/analytics")
async def get_premium_analytics(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get premium analytics"""
    if not premium_service.check_premium_access(current_user.id):
        raise HTTPException(status_code=403, detail="Premium access required")
    
    return premium_service.get_premium_analytics(current_user.id)

@app.get("/premium/experts")
async def get_expert_recommendations(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get expert recommendations"""
    if not premium_service.check_premium_access(current_user.id):
        raise HTTPException(status_code=403, detail="Premium access required")
    
    user_interests = interest_service.get_user_interests(db, current_user.id)
    return premium_service.get_expert_recommendations(user_interests)

@app.post("/premium/scrape")
async def deep_web_scraping(
    url: str,
    depth: int = 2,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Perform deep web scraping (premium feature)"""
    if not premium_service.check_premium_access(current_user.id):
        raise HTTPException(status_code=403, detail="Premium access required")
    
    return premium_service.deep_web_scraping(url, depth)

@app.get("/premium/academic-papers")
async def search_academic_papers(
    query: str,
    max_results: int = 20,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Search academic papers (premium feature)"""
    if not premium_service.check_premium_access(current_user.id):
        raise HTTPException(status_code=403, detail="Premium access required")
    
    return premium_service.search_academic_papers(query, max_results)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
