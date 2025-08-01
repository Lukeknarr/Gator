from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for many-to-many relationship between content and tags
content_tags = Table(
    'content_tags',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interests = relationship("UserInterest", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")

class UserInterest(Base):
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, index=True)
    weight = Column(Float, default=1.0)
    source = Column(String)  # 'manual', 'passive', 'onboarding'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interests")

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    source = Column(String, index=True)  # 'rss', 'substack', 'arxiv', 'youtube'
    author = Column(String)
    published_at = Column(DateTime(timezone=True))
    summary = Column(Text)
    content_type = Column(String)  # 'article', 'podcast', 'video', 'paper'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tags = relationship("Tag", secondary=content_tags, back_populates="content")
    interactions = relationship("UserInteraction", back_populates="content")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # 'topic', 'domain', 'skill'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content = relationship("Content", secondary=content_tags, back_populates="tags")

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    interaction_type = Column(String)  # 'view', 'like', 'dislike', 'share', 'bookmark'
    duration = Column(Integer)  # seconds spent on content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    score = Column(Float)
    algorithm = Column(String)  # 'tfidf', 'collaborative', 'graph'
    served_at = Column(DateTime(timezone=True), server_default=func.now())
    clicked = Column(Boolean, default=False) 