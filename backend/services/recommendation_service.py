from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from models import User, Content, Tag, UserInterest, UserInteraction, Recommendation
from schemas import ContentResponse, FeedbackRequest

class RecommendationService:
    def __init__(self):
        self.mock_vectorizer = "mock"
    
    def get_recommendations(self, db: Session, user_id: int, limit: int = 20) -> List[ContentResponse]:
        """Get mock personalized recommendations"""
        # Get user interests
        user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
        interest_topics = [interest.topic for interest in user_interests]
        
        if not interest_topics:
            # If no interests, return recent content
            return self._get_recent_content(db, limit)
        
        # Get content with tags
        content_with_tags = db.query(Content).join(Content.tags).all()
        
        if not content_with_tags:
            return []
        
        # Calculate mock scores
        mock_scores = self._calculate_mock_scores(content_with_tags, interest_topics)
        
        # Sort by score and get top recommendations
        sorted_content = sorted(content_with_tags, key=lambda x: mock_scores.get(x.id, 0), reverse=True)
        
        # Store recommendations
        for i, content in enumerate(sorted_content[:limit]):
            recommendation = Recommendation(
                user_id=user_id,
                content_id=content.id,
                score=mock_scores.get(content.id, 0),
                algorithm="mock_hybrid"
            )
            db.add(recommendation)
        
        db.commit()
        
        return [ContentResponse.from_orm(content) for content in sorted_content[:limit]]
    
    def _calculate_mock_scores(self, content_list: List[Content], interest_topics: List[str]) -> Dict[int, float]:
        """Calculate mock similarity scores"""
        if not content_list:
            return {}
        
        scores = {}
        
        for content in content_list:
            # Mock scoring based on simple text matching
            score = 0.0
            
            # Combine content text
            content_text = f"{content.title or ''} {content.summary or ''}"
            content_text_lower = content_text.lower()
            
            # Check for interest topic matches
            for topic in interest_topics:
                if topic.lower() in content_text_lower:
                    score += 0.5
            
            # Add some randomness for variety
            score += random.uniform(0, 0.3)
            
            # Normalize score
            score = min(1.0, score)
            scores[content.id] = score
        
        return scores
    
    def _get_recent_content(self, db: Session, limit: int) -> List[ContentResponse]:
        """Get recent content when no interests are available"""
        recent_content = db.query(Content).order_by(desc(Content.created_at)).limit(limit).all()
        return [ContentResponse.from_orm(content) for content in recent_content]
    
    def submit_feedback(self, db: Session, user_id: int, feedback: FeedbackRequest) -> Dict[str, Any]:
        """Submit user feedback on content"""
        try:
            # Create interaction record
            interaction = UserInteraction(
                user_id=user_id,
                content_id=feedback.content_id,
                interaction_type=feedback.feedback_type,
                rating=feedback.rating,
                metadata={
                    "feedback_text": feedback.feedback_text,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            db.add(interaction)
            db.commit()
            
            # Update recommendation scores based on feedback
            self._update_recommendation_scores(db, user_id, feedback)
            
            return {
                "message": "Feedback submitted successfully",
                "interaction_id": interaction.id
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
    
    def _update_recommendation_scores(self, db: Session, user_id: int, feedback: FeedbackRequest):
        """Update recommendation scores based on feedback"""
        try:
            # Find existing recommendation
            recommendation = db.query(Recommendation).filter(
                Recommendation.user_id == user_id,
                Recommendation.content_id == feedback.content_id
            ).first()
            
            if recommendation:
                # Adjust score based on feedback
                if feedback.feedback_type == "like":
                    recommendation.score += 0.1
                elif feedback.feedback_type == "dislike":
                    recommendation.score -= 0.1
                elif feedback.feedback_type == "rating" and feedback.rating:
                    # Normalize rating to 0-1 scale
                    normalized_rating = feedback.rating / 5.0
                    recommendation.score = normalized_rating
                
                # Ensure score stays within bounds
                recommendation.score = max(0.0, min(1.0, recommendation.score))
                
                db.commit()
                
        except Exception as e:
            print(f"Error updating recommendation scores: {e}")
    
    def get_exploration_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[ContentResponse]:
        """Get exploration recommendations (diverse content)"""
        try:
            # Get user's current interests
            user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
            current_topics = [interest.topic for interest in user_interests]
            
            # Get all content
            all_content = db.query(Content).join(Content.tags).all()
            
            if not all_content:
                return []
            
            # Find content that doesn't match current interests
            diverse_content = []
            for content in all_content:
                content_text = f"{content.title or ''} {content.summary or ''}".lower()
                
                # Check if content is different from current interests
                is_diverse = True
                for topic in current_topics:
                    if topic.lower() in content_text:
                        is_diverse = False
                        break
                
                if is_diverse:
                    diverse_content.append(content)
            
            # If no diverse content, return random content
            if not diverse_content:
                diverse_content = random.sample(all_content, min(len(all_content), limit))
            
            # Limit results
            diverse_content = diverse_content[:limit]
            
            return [ContentResponse.from_orm(content) for content in diverse_content]
            
        except Exception as e:
            print(f"Error getting exploration recommendations: {e}")
            return []
    
    def get_trending_content(self, db: Session, limit: int = 10) -> List[ContentResponse]:
        """Get trending content based on interactions"""
        try:
            # Get content with most interactions
            trending_content = db.query(Content).join(UserInteraction).group_by(Content.id).order_by(
                func.count(UserInteraction.id).desc()
            ).limit(limit).all()
            
            return [ContentResponse.from_orm(content) for content in trending_content]
            
        except Exception as e:
            print(f"Error getting trending content: {e}")
            return []
    
    def get_personalized_feed(self, db: Session, user_id: int, limit: int = 20) -> List[ContentResponse]:
        """Get personalized feed combining multiple recommendation types"""
        try:
            # Get different types of recommendations
            personalized = self.get_recommendations(db, user_id, limit // 2)
            exploration = self.get_exploration_recommendations(db, user_id, limit // 4)
            trending = self.get_trending_content(db, limit // 4)
            
            # Combine and deduplicate
            all_recommendations = personalized + exploration + trending
            seen_ids = set()
            unique_recommendations = []
            
            for rec in all_recommendations:
                if rec.id not in seen_ids:
                    unique_recommendations.append(rec)
                    seen_ids.add(rec.id)
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting personalized feed: {e}")
            return [] 