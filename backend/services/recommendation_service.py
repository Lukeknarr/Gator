from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any
from datetime import datetime
import random

from models import User, UserInterest, Content, UserInteraction, Recommendation
from schemas import ContentResponse, FeedbackRequest

class RecommendationService:
    def __init__(self):
        pass
    
    def get_recommendations(self, db: Session, user_id: int, limit: int = 20) -> List[ContentResponse]:
        """Get personalized recommendations for user"""
        try:
            # Get user's interests
            user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
            
            if not user_interests:
                # If no interests, return recent content
                return self._get_recent_content(db, limit)
            
            # Get interest topics
            interest_topics = [interest.topic for interest in user_interests]
            
            # Get all content
            all_content = db.query(Content).all()
            
            if not all_content:
                return []
            
            # Calculate mock scores based on interests
            content_scores = self._calculate_mock_scores(all_content, interest_topics)
            
            # Sort by score and limit
            sorted_content = sorted(all_content, key=lambda x: content_scores.get(x.id, 0), reverse=True)
            top_content = sorted_content[:limit]
            
            return [ContentResponse.from_orm(content) for content in top_content]
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return self._get_recent_content(db, limit)
    
    def _calculate_mock_scores(self, content_list: List[Content], interest_topics: List[str]) -> Dict[int, float]:
        """Calculate mock recommendation scores based on interests"""
        scores = {}
        
        for content in content_list:
            score = 0.0
            content_text = f"{content.title or ''} {content.summary or ''}".lower()
            
            # Score based on interest matches
            for topic in interest_topics:
                if topic.lower() in content_text:
                    score += 0.3
            
            # Add some randomness
            score += random.uniform(0, 0.2)
            
            # Ensure score is between 0 and 1
            score = min(1.0, max(0.0, score))
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
                interaction_type=feedback.interaction_type,
                duration=feedback.duration
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
                if feedback.interaction_type == "like":
                    recommendation.score += 0.1
                elif feedback.interaction_type == "dislike":
                    recommendation.score -= 0.1
                
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
            all_content = db.query(Content).all()
            
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
            return self.get_recommendations(db, user_id, limit) 