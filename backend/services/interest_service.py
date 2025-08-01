from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json

from ..models import User, UserInterest
from ..schemas import UserOnboarding, InterestCreate, InterestResponse, UserDataExport

class InterestService:
    def complete_onboarding(self, db: Session, user: User, onboarding_data: UserOnboarding) -> User:
        """Complete user onboarding by adding initial interests"""
        # Add interests from onboarding
        for interest in onboarding_data.interests:
            user_interest = UserInterest(
                user_id=user.id,
                topic=interest,
                weight=1.0,
                source="onboarding"
            )
            db.add(user_interest)
        
        db.commit()
        db.refresh(user)
        return user
    
    def get_user_interests(self, db: Session, user_id: int) -> List[InterestResponse]:
        """Get all interests for a user"""
        interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
        return [InterestResponse.from_orm(interest) for interest in interests]
    
    def add_interest(self, db: Session, user_id: int, interest: InterestCreate) -> InterestResponse:
        """Add a new interest to user's graph"""
        # Check if interest already exists
        existing = db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.topic == interest.topic
        ).first()
        
        if existing:
            # Update weight if interest exists
            existing.weight = min(existing.weight + 0.1, 2.0)
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return InterestResponse.from_orm(existing)
        
        # Create new interest
        user_interest = UserInterest(
            user_id=user_id,
            topic=interest.topic,
            weight=interest.weight,
            source=interest.source
        )
        db.add(user_interest)
        db.commit()
        db.refresh(user_interest)
        return InterestResponse.from_orm(user_interest)
    
    def update_interest_weight(self, db: Session, user_id: int, topic: str, weight_change: float):
        """Update interest weight based on user interaction"""
        interest = db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.topic == topic
        ).first()
        
        if interest:
            interest.weight = max(0.1, min(2.0, interest.weight + weight_change))
            interest.updated_at = datetime.utcnow()
            db.commit()
    
    def get_interest_graph(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get user's interest graph for visualization"""
        interests = self.get_user_interests(db, user_id)
        
        # Create graph structure
        nodes = []
        edges = []
        
        for interest in interests:
            nodes.append({
                "id": interest.id,
                "label": interest.topic,
                "weight": interest.weight,
                "source": interest.source
            })
        
        # For now, create simple connections between interests
        # In a real implementation, this would use NLP to find semantic connections
        for i, interest1 in enumerate(interests):
            for j, interest2 in enumerate(interests[i+1:], i+1):
                # Simple similarity based on shared words
                words1 = set(interest1.topic.lower().split())
                words2 = set(interest2.topic.lower().split())
                similarity = len(words1.intersection(words2)) / len(words1.union(words2)) if words1.union(words2) else 0
                
                if similarity > 0.1:  # Threshold for connection
                    edges.append({
                        "source": interest1.id,
                        "target": interest2.id,
                        "weight": similarity
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def export_user_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Export user data in JSON format"""
        user = db.query(User).filter(User.id == user_id).first()
        interests = self.get_user_interests(db, user_id)
        
        # Get user interactions
        interactions = db.query(UserInteraction).filter(UserInteraction.user_id == user_id).all()
        interaction_data = []
        for interaction in interactions:
            interaction_data.append({
                "content_id": interaction.content_id,
                "interaction_type": interaction.interaction_type,
                "duration": interaction.duration,
                "created_at": interaction.created_at.isoformat()
            })
        
        # Get recommendations served
        recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
        recommendation_data = []
        for rec in recommendations:
            recommendation_data.append({
                "content_id": rec.content_id,
                "score": rec.score,
                "algorithm": rec.algorithm,
                "served_at": rec.served_at.isoformat(),
                "clicked": rec.clicked
            })
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": user.created_at.isoformat()
            },
            "interests": [interest.dict() for interest in interests],
            "interactions": interaction_data,
            "recommendations": recommendation_data,
            "export_date": datetime.utcnow().isoformat()
        } 