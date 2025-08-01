import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from datetime import datetime, timedelta
import json
import os

class LJKRecommendationEngine:
    """
    LJK Recommendation Engine - Advanced recommendation system for Gator
    Combines multiple algorithms for personalized content discovery
    """
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.nmf_model = None
        self.user_embeddings = {}
        self.content_embeddings = {}
        self.interest_graph = nx.Graph()
        
    def build_interest_graph(self, user_interests: List[Dict], content_tags: List[Dict]) -> nx.Graph:
        """Build a knowledge graph connecting interests and content"""
        graph = nx.Graph()
        
        # Add user interest nodes
        for interest in user_interests:
            graph.add_node(f"interest_{interest['id']}", 
                          type='interest', 
                          name=interest['topic'],
                          weight=interest['weight'])
        
        # Add content nodes
        for content in content_tags:
            graph.add_node(f"content_{content['id']}", 
                          type='content',
                          title=content['title'],
                          source=content['source'])
            
            # Connect content to its tags
            for tag in content['tags']:
                graph.add_node(f"tag_{tag['id']}", 
                              type='tag',
                              name=tag['name'])
                graph.add_edge(f"content_{content['id']}", f"tag_{tag['id']}", weight=1.0)
        
        # Connect interests to related tags
        for interest in user_interests:
            interest_text = interest['topic'].lower()
            for content in content_tags:
                for tag in content['tags']:
                    tag_text = tag['name'].lower()
                    # Simple similarity check
                    if any(word in tag_text for word in interest_text.split()) or \
                       any(word in interest_text for word in tag_text.split()):
                        graph.add_edge(f"interest_{interest['id']}", f"tag_{tag['id']}", 
                                     weight=interest['weight'])
        
        self.interest_graph = graph
        return graph
    
    def calculate_tfidf_similarity(self, user_interests: List[str], content_data: List[Dict]) -> Dict[int, float]:
        """Calculate TF-IDF similarity between user interests and content"""
        if not content_data:
            return {}
        
        # Prepare content text
        content_texts = []
        for content in content_data:
            text_parts = [content['title']]
            if content.get('summary'):
                text_parts.append(content['summary'])
            for tag in content.get('tags', []):
                text_parts.append(tag['name'])
            content_texts.append(" ".join(text_parts))
        
        # Create TF-IDF vectors
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(content_texts)
            interest_text = " ".join(user_interests)
            interest_vector = self.tfidf_vectorizer.transform([interest_text])
            
            # Calculate similarities
            similarities = cosine_similarity(interest_vector, tfidf_matrix).flatten()
            
            return {content['id']: float(similarities[i]) for i, content in enumerate(content_data)}
        except Exception as e:
            print(f"TF-IDF calculation error: {e}")
            return {}
    
    def calculate_collaborative_scores(self, user_id: int, user_interactions: List[Dict], 
                                     content_data: List[Dict]) -> Dict[int, float]:
        """Calculate collaborative filtering scores"""
        if not user_interactions:
            return {}
        
        # Create user-item matrix
        user_item_matrix = {}
        for interaction in user_interactions:
            user = interaction['user_id']
            item = interaction['content_id']
            rating = 1.0 if interaction['interaction_type'] == 'like' else 0.5
            
            if user not in user_item_matrix:
                user_item_matrix[user] = {}
            user_item_matrix[user][item] = rating
        
        # Find similar users
        similar_users = self._find_similar_users(user_id, user_item_matrix)
        
        # Calculate scores based on similar users' preferences
        scores = {}
        for content in content_data:
            content_id = content['id']
            score = 0.0
            total_weight = 0.0
            
            for similar_user, similarity in similar_users:
                if content_id in user_item_matrix.get(similar_user, {}):
                    score += similarity * user_item_matrix[similar_user][content_id]
                    total_weight += similarity
            
            if total_weight > 0:
                scores[content_id] = score / total_weight
            else:
                scores[content_id] = 0.0
        
        return scores
    
    def _find_similar_users(self, user_id: int, user_item_matrix: Dict) -> List[Tuple[int, float]]:
        """Find users with similar preferences"""
        if user_id not in user_item_matrix:
            return []
        
        user_items = set(user_item_matrix[user_id].keys())
        similar_users = []
        
        for other_user, other_items in user_item_matrix.items():
            if other_user == user_id:
                continue
            
            other_item_set = set(other_items.keys())
            intersection = len(user_items & other_item_set)
            union = len(user_items | other_item_set)
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # Threshold for similarity
                    similar_users.append((other_user, similarity))
        
        return sorted(similar_users, key=lambda x: x[1], reverse=True)[:10]
    
    def calculate_graph_based_scores(self, user_id: int, content_data: List[Dict]) -> Dict[int, float]:
        """Calculate scores using graph-based algorithms"""
        if not self.interest_graph.nodes():
            return {}
        
        scores = {}
        
        # Use Personalized PageRank
        try:
            pagerank_scores = nx.pagerank(self.interest_graph, personalization={
                f"interest_{user_id}": 1.0
            })
            
            for content in content_data:
                content_node = f"content_{content['id']}"
                if content_node in pagerank_scores:
                    scores[content['id']] = pagerank_scores[content_node]
                else:
                    scores[content['id']] = 0.0
                    
        except Exception as e:
            print(f"Graph-based scoring error: {e}")
            return {}
        
        return scores
    
    def calculate_cross_domain_scores(self, user_interests: List[str], 
                                    content_data: List[Dict]) -> Dict[int, float]:
        """Calculate cross-domain discovery scores"""
        scores = {}
        
        # Extract interest domains
        interest_domains = set()
        for interest in user_interests:
            domain = self._extract_domain(interest)
            interest_domains.add(domain)
        
        for content in content_data:
            content_domains = set()
            for tag in content.get('tags', []):
                domain = self._extract_domain(tag['name'])
                content_domains.add(domain)
            
            # Calculate novelty (how many new domains)
            new_domains = content_domains - interest_domains
            novelty_score = len(new_domains) / max(len(content_domains), 1)
            
            # Calculate bridge score (content that connects domains)
            if len(content_domains) > 1:
                bridge_score = 0.5
            else:
                bridge_score = 0.0
            
            # Combine novelty and bridge scores
            cross_domain_score = 0.7 * novelty_score + 0.3 * bridge_score
            scores[content['id']] = cross_domain_score
        
        return scores
    
    def _extract_domain(self, text: str) -> str:
        """Extract domain from text"""
        text_lower = text.lower()
        
        # Simple domain mapping
        if any(word in text_lower for word in ['tech', 'software', 'ai', 'machine learning']):
            return 'technology'
        elif any(word in text_lower for word in ['politics', 'government', 'policy']):
            return 'politics'
        elif any(word in text_lower for word in ['science', 'research', 'study']):
            return 'science'
        elif any(word in text_lower for word in ['business', 'startup', 'finance']):
            return 'business'
        elif any(word in text_lower for word in ['health', 'medical', 'medicine']):
            return 'health'
        else:
            return 'general'
    
    def get_hybrid_recommendations(self, user_id: int, user_interests: List[Dict], 
                                 content_data: List[Dict], user_interactions: List[Dict],
                                 limit: int = 20) -> List[Dict]:
        """Get hybrid recommendations combining multiple algorithms"""
        
        # Prepare data
        interest_topics = [interest['topic'] for interest in user_interests]
        
        # Calculate scores from different algorithms
        tfidf_scores = self.calculate_tfidf_similarity(interest_topics, content_data)
        collaborative_scores = self.calculate_collaborative_scores(user_id, user_interactions, content_data)
        graph_scores = self.calculate_graph_based_scores(user_id, content_data)
        cross_domain_scores = self.calculate_cross_domain_scores(interest_topics, content_data)
        
        # Combine scores with weights
        final_scores = {}
        for content in content_data:
            content_id = content['id']
            
            tfidf_score = tfidf_scores.get(content_id, 0.0)
            collaborative_score = collaborative_scores.get(content_id, 0.0)
            graph_score = graph_scores.get(content_id, 0.0)
            cross_domain_score = cross_domain_scores.get(content_id, 0.0)
            
            # Weighted combination
            final_score = (
                0.4 * tfidf_score +
                0.3 * collaborative_score +
                0.2 * graph_score +
                0.1 * cross_domain_score
            )
            
            final_scores[content_id] = final_score
        
        # Sort by score and return top recommendations
        sorted_content = sorted(content_data, key=lambda x: final_scores.get(x['id'], 0), reverse=True)
        
        recommendations = []
        for content in sorted_content[:limit]:
            recommendation = {
                'content': content,
                'score': final_scores.get(content['id'], 0),
                'algorithm': 'hybrid',
                'reasoning': self._generate_reasoning(content, user_interests, final_scores.get(content['id'], 0))
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_reasoning(self, content: Dict, user_interests: List[Dict], score: float) -> str:
        """Generate explanation for recommendation"""
        content_tags = [tag['name'].lower() for tag in content.get('tags', [])]
        interest_topics = [interest['topic'].lower() for interest in user_interests]
        
        # Find matching interests
        matching_interests = []
        for interest in interest_topics:
            for tag in content_tags:
                if any(word in tag for word in interest.split()) or any(word in interest for word in tag.split()):
                    matching_interests.append(interest)
        
        if matching_interests:
            return f"Recommended because you're interested in: {', '.join(matching_interests[:2])}"
        elif score > 0.7:
            return "High-quality content that might interest you"
        else:
            return "Exploration recommendation to discover new topics"
    
    def update_user_embeddings(self, user_id: int, interactions: List[Dict]):
        """Update user embeddings based on interactions"""
        # Simple embedding update based on interaction patterns
        embedding = np.zeros(100)  # 100-dimensional embedding
        
        for interaction in interactions:
            if interaction['interaction_type'] == 'like':
                embedding += 0.1
            elif interaction['interaction_type'] == 'dislike':
                embedding -= 0.1
            elif interaction['interaction_type'] == 'view':
                embedding += 0.05
        
        self.user_embeddings[user_id] = embedding
    
    def get_exploration_recommendations(self, user_interests: List[str], 
                                      content_data: List[Dict], limit: int = 10) -> List[Dict]:
        """Get recommendations that explore new topics"""
        user_interest_set = set(interest.lower() for interest in user_interests)
        exploration_content = []
        
        for content in content_data:
            content_tags = [tag['name'].lower() for tag in content.get('tags', [])]
            
            # Calculate how many new topics this content introduces
            new_topics = set(content_tags) - user_interest_set
            exploration_score = len(new_topics) / max(len(content_tags), 1)
            
            if exploration_score > 0.3:  # Threshold for exploration
                exploration_content.append({
                    'content': content,
                    'exploration_score': exploration_score,
                    'new_topics': list(new_topics)
                })
        
        # Sort by exploration score
        exploration_content.sort(key=lambda x: x['exploration_score'], reverse=True)
        
        return exploration_content[:limit]
    
    def get_connection_recommendations(self, user_interests: List[str], 
                                     content_data: List[Dict], limit: int = 10) -> List[Dict]:
        """Get recommendations that connect seemingly unrelated interests"""
        connection_recommendations = []
        
        for content in content_data:
            content_tags = [tag['name'].lower() for tag in content.get('tags', [])]
            
            # Find content that connects multiple user interests
            connected_interests = []
            for interest in user_interests:
                interest_lower = interest.lower()
                for tag in content_tags:
                    if any(word in tag for word in interest_lower.split()) or \
                       any(word in interest_lower for word in tag.split()):
                        connected_interests.append(interest)
            
            if len(connected_interests) > 1:
                connection_recommendations.append({
                    'content': content,
                    'connected_interests': connected_interests,
                    'connection_score': len(connected_interests) / len(user_interests)
                })
        
        # Sort by connection score
        connection_recommendations.sort(key=lambda x: x['connection_score'], reverse=True)
        
        return connection_recommendations[:limit]

# Example usage
if __name__ == "__main__":
    engine = LJKRecommendationEngine()
    
    # Example data
    user_interests = [
        {'id': 1, 'topic': 'artificial intelligence', 'weight': 1.0},
        {'id': 2, 'topic': 'climate change', 'weight': 0.8}
    ]
    
    content_data = [
        {
            'id': 1,
            'title': 'AI and Climate Change Solutions',
            'tags': [
                {'id': 1, 'name': 'artificial intelligence'},
                {'id': 2, 'name': 'climate change'},
                {'id': 3, 'name': 'technology'}
            ]
        }
    ]
    
    # Build graph and get recommendations
    graph = engine.build_interest_graph(user_interests, content_data)
    recommendations = engine.get_hybrid_recommendations(
        user_id=1,
        user_interests=user_interests,
        content_data=content_data,
        user_interactions=[],
        limit=10
    )
    
    print("Recommendations:", recommendations)
