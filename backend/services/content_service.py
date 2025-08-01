from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime

from ..models import Content, Tag, UserInteraction
from ..schemas import ContentResponse, SearchRequest

class ContentService:
    def get_content(self, db: Session, content_id: int) -> ContentResponse:
        """Get specific content by ID"""
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise ValueError("Content not found")
        return ContentResponse.from_orm(content)
    
    def search_content(self, db: Session, query: str, limit: int = 20) -> List[ContentResponse]:
        """Search content across all sources"""
        # Simple text search in title and summary
        search_results = db.query(Content).filter(
            func.lower(Content.title).contains(func.lower(query)) |
            func.lower(Content.summary).contains(func.lower(query))
        ).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content in search_results]
    
    def get_content_by_source(self, db: Session, source: str, limit: int = 20) -> List[ContentResponse]:
        """Get content from specific source"""
        content = db.query(Content).filter(Content.source == source).order_by(
            desc(Content.created_at)
        ).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content in content]
    
    def get_content_by_type(self, db: Session, content_type: str, limit: int = 20) -> List[ContentResponse]:
        """Get content by type (article, podcast, video, paper)"""
        content = db.query(Content).filter(Content.content_type == content_type).order_by(
            desc(Content.created_at)
        ).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content in content]
    
    def get_popular_content(self, db: Session, limit: int = 20) -> List[ContentResponse]:
        """Get most popular content based on interactions"""
        popular_content = db.query(
            Content,
            func.count(UserInteraction.id).label('interaction_count')
        ).join(UserInteraction).group_by(Content.id).order_by(
            desc('interaction_count')
        ).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content, _ in popular_content]
    
    def get_recent_content(self, db: Session, limit: int = 20) -> List[ContentResponse]:
        """Get most recent content"""
        recent_content = db.query(Content).order_by(
            desc(Content.created_at)
        ).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content in recent_content]
    
    def get_content_by_tags(self, db: Session, tags: List[str], limit: int = 20) -> List[ContentResponse]:
        """Get content that has specific tags"""
        content = db.query(Content).join(Content.tags).filter(
            Tag.name.in_(tags)
        ).distinct().order_by(desc(Content.created_at)).limit(limit).all()
        
        return [ContentResponse.from_orm(content) for content in content]
    
    def get_content_statistics(self, db: Session) -> Dict[str, Any]:
        """Get content statistics"""
        total_content = db.query(func.count(Content.id)).scalar()
        content_by_source = db.query(
            Content.source,
            func.count(Content.id).label('count')
        ).group_by(Content.source).all()
        
        content_by_type = db.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).group_by(Content.content_type).all()
        
        return {
            "total_content": total_content,
            "by_source": {source: count for source, count in content_by_source},
            "by_type": {content_type: count for content_type, count in content_by_type}
        } 