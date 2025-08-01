from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Interest schemas
class InterestBase(BaseModel):
    topic: str
    weight: Optional[float] = 1.0
    source: Optional[str] = "manual"

class InterestCreate(InterestBase):
    pass

class InterestResponse(InterestBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Content schemas
class TagResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    
    class Config:
        from_attributes = True

class ContentResponse(BaseModel):
    id: int
    title: str
    url: str
    source: str
    author: Optional[str]
    published_at: Optional[datetime]
    summary: Optional[str]
    content_type: str
    tags: List[TagResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Onboarding schemas
class UserOnboarding(BaseModel):
    interests: List[str]
    reading_preferences: List[str]  # ['articles', 'podcasts', 'videos', 'papers']
    time_availability: str  # 'low', 'medium', 'high'
    exploration_level: str  # 'conservative', 'balanced', 'adventurous'

# Recommendation schemas
class RecommendationRequest(BaseModel):
    limit: Optional[int] = 20
    algorithm: Optional[str] = "hybrid"  # 'tfidf', 'collaborative', 'graph', 'hybrid'

class RecommendationResponse(BaseModel):
    content: ContentResponse
    score: float
    reasoning: Optional[str]

# Feedback schemas
class FeedbackRequest(BaseModel):
    content_id: int
    interaction_type: str  # 'like', 'dislike', 'view', 'share'
    duration: Optional[int] = None  # seconds spent
    feedback_text: Optional[str] = None

# Search schemas
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20
    content_types: Optional[List[str]] = None
    sources: Optional[List[str]] = None

# Export schemas
class UserDataExport(BaseModel):
    user: UserResponse
    interests: List[InterestResponse]
    interactions: List[dict]
    recommendations: List[dict]
    export_date: datetime 