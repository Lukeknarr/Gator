from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from datetime import datetime, timedelta

from ..models import User, Content, Tag, UserInterest, UserInteraction, Recommendation
from ..schemas import ContentResponse, FeedbackRequest

class RecommendationService:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def get_recommendations(self, db: Session, user_id: int, limit: int = 20) -> List[ContentResponse]:
        """Get personalized recommendations using hybrid approach"""
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
        
        # Calculate scores using multiple algorithms
        tfidf_scores = self._calculate_tfidf_scores(content_with_tags, interest_topics)
        collaborative_scores = self._calculate_collaborative_scores(db, user_id, content_with_tags)
        
        # Combine scores (hybrid approach)
        final_scores = {}
        for content in content_with_tags:
            tfidf_score = tfidf_scores.get(content.id, 0)
            collaborative_score = collaborative_scores.get(content.id, 0)
            
            # Weighted combination
            final_score = 0.6 * tfidf_score + 0.4 * collaborative_score
            final_scores[content.id] = final_score
        
        # Sort by score and get top recommendations
        sorted_content = sorted(content_with_tags, key=lambda x: final_scores.get(x.id, 0), reverse=True)
        
        # Store recommendations
        for i, content in enumerate(sorted_content[:limit]):
            recommendation = Recommendation(
                user_id=user_id,
                content_id=content.id,
                score=final_scores.get(content.id, 0),
                algorithm="hybrid"
            )
            db.add(recommendation)
        
        db.commit()
        
        return [ContentResponse.from_orm(content) for content in sorted_content[:limit]]
    
    def _calculate_tfidf_scores(self, content_list: List[Content], interest_topics: List[str]) -> Dict[int, float]:
        """Calculate TF-IDF similarity scores"""
        if not content_list:
            return {}
        
        # Prepare text for TF-IDF
        content_texts = []
        for content in content_list:
            # Combine title, summary, and tags
            text_parts = [content.title or ""]
            if content.summary:
                text_parts.append(content.summary)
            for tag in content.tags:
                text_parts.append(tag.name)
            content_texts.append(" ".join(text_parts))
        
        # Create TF-IDF vectors
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(content_texts)
            interest_text = " ".join(interest_topics)
            interest_vector = self.tfidf_vectorizer.transform([interest_text])
            
            # Calculate similarities
            similarities = cosine_similarity(interest_vector, tfidf_matrix).flatten()
            
            return {content.id: float(similarities[i]) for i, content in enumerate(content_list)}
        except Exception as e:
            print(f"TF-IDF calculation error: {e}")
            return {}
    
    def _calculate_collaborative_scores(self, db: Session, user_id: int, content_list: List[Content]) -> Dict[int, float]:
        """Calculate collaborative filtering scores"""
        if not content_list:
            return {}
        
        # Get users with similar interests
        user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
        user_topics = {interest.topic for interest in user_interests}
        
        # Find users with overlapping interests
        similar_users = db.query(UserInterest.user_id).filter(
            UserInterest.topic.in_(user_topics),
            UserInterest.user_id != user_id
        ).distinct().all()
        
        similar_user_ids = [user_id for (user_id,) in similar_users]
        
        if not similar_user_ids:
            return {}
        
        # Get content liked by similar users
        liked_content = db.query(UserInteraction.content_id, func.count(UserInteraction.id).label('like_count')).filter(
            UserInteraction.user_id.in_(similar_user_ids),
            UserInteraction.interaction_type == 'like'
        ).group_by(UserInteraction.content_id).all()
        
        # Calculate scores based on popularity among similar users
        scores = {}
        total_likes = sum(count for _, count in liked_content)
        
        for content_id, like_count in liked_content:
            if total_likes > 0:
                scores[content_id] = like_count / total_likes
            else:
                scores[content_id] = 0
        
        return scores
    
    def _get_recent_content(self, db: Session, limit: int) -> List[ContentResponse]:
        """Get recent content when user has no interests"""
        recent_content = db.query(Content).order_by(desc(Content.created_at)).limit(limit).all()
        return [ContentResponse.from_orm(content) for content in recent_content]
    
    def submit_feedback(self, db: Session, user_id: int, feedback: FeedbackRequest) -> Dict[str, Any]:
        """Process user feedback and update interest weights"""
        # Record the interaction
        interaction = UserInteraction(
            user_id=user_id,
            content_id=feedback.content_id,
            interaction_type=feedback.interaction_type,
            duration=feedback.duration
        )
        db.add(interaction)
        
        # Get content and its tags
        content = db.query(Content).filter(Content.id == feedback.content_id).first()
        if not content:
            raise ValueError("Content not found")
        
        # Update interest weights based on feedback
        weight_change = 0.0
        if feedback.interaction_type == 'like':
            weight_change = 0.1
        elif feedback.interaction_type == 'dislike':
            weight_change = -0.1
        elif feedback.interaction_type == 'view':
            weight_change = 0.05
        
        # Update weights for content tags that match user interests
        for tag in content.tags:
            # Check if user has this interest
            user_interest = db.query(UserInterest).filter(
                UserInterest.user_id == user_id,
                UserInterest.topic.ilike(f"%{tag.name}%")
            ).first()
            
            if user_interest:
                user_interest.weight = max(0.1, min(2.0, user_interest.weight + weight_change))
                user_interest.updated_at = datetime.utcnow()
        
        # Update recommendation if it exists
        recommendation = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.content_id == feedback.content_id
        ).first()
        
        if recommendation:
            recommendation.clicked = feedback.interaction_type in ['like', 'view']
        
        db.commit()
        
        return {
            "message": "Feedback recorded successfully",
            "content_id": feedback.content_id,
            "interaction_type": feedback.interaction_type
        }
    
    def get_exploration_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[ContentResponse]:
        """Get recommendations that explore new topics"""
        # Get user's current interests
        user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
        user_topics = {interest.topic.lower() for interest in user_interests}
        
        # Find content with tags that don't match current interests
        all_content = db.query(Content).join(Content.tags).all()
        exploration_content = []
        
        for content in all_content:
            content_tags = {tag.name.lower() for tag in content.tags}
            # Check if content has tags not in user interests
            new_topics = content_tags - user_topics
            if new_topics:
                exploration_content.append((content, len(new_topics)))
        
        # Sort by number of new topics and get top recommendations
        exploration_content.sort(key=lambda x: x[1], reverse=True)
        
        return [ContentResponse.from_orm(content) for content, _ in exploration_content[:limit]] 