import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from transformers import pipeline
import torch
from typing import List, Dict, Any, Tuple, Optional
import json
from collections import defaultdict
import random

class CrossInterestConnectionMap:
    """
    Cross-interest connection map service for Gator
    Suggests novel connections between seemingly unrelated topics
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.embedding_model = None
        self.similarity_threshold = 0.3
        self.novelty_threshold = 0.7
        self.connection_cache = {}
        
    def load_embedding_model(self):
        """Load sentence embedding model for semantic similarity"""
        if not self.embedding_model:
            print("Loading embedding model for connection mapping...")
            self.embedding_model = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2",
                device=0 if torch.cuda.is_available() else -1
            )
    
    def build_connection_graph(self, user_interests: List[Dict], content_data: List[Dict]) -> nx.Graph:
        """Build a graph of interests and content connections"""
        self.graph.clear()
        
        # Add user interests as nodes
        for interest in user_interests:
            self.graph.add_node(
                interest['name'],
                type='interest',
                weight=interest.get('weight', 1.0),
                category=interest.get('category', 'general')
            )
        
        # Add content as nodes
        for content in content_data:
            content_id = f"content_{content['id']}"
            self.graph.add_node(
                content_id,
                type='content',
                title=content['title'],
                tags=content.get('tags', []),
                category=content.get('category', 'general')
            )
        
        # Create connections between interests and content
        self._create_interest_content_connections(user_interests, content_data)
        
        # Create cross-interest connections
        self._create_cross_interest_connections(user_interests)
        
        return self.graph
    
    def _create_interest_content_connections(self, user_interests: List[Dict], content_data: List[Dict]):
        """Create connections between interests and content"""
        for interest in user_interests:
            interest_name = interest['name'].lower()
            
            for content in content_data:
                content_id = f"content_{content['id']}"
                
                # Check tag similarity
                content_tags = [tag.lower() for tag in content.get('tags', [])]
                similarity_score = self._calculate_tag_similarity(interest_name, content_tags)
                
                if similarity_score > self.similarity_threshold:
                    self.graph.add_edge(
                        interest['name'],
                        content_id,
                        weight=similarity_score,
                        type='interest_content'
                    )
    
    def _create_cross_interest_connections(self, user_interests: List[Dict]):
        """Create connections between different interests"""
        for i, interest1 in enumerate(user_interests):
            for j, interest2 in enumerate(user_interests[i+1:], i+1):
                similarity = self._calculate_interest_similarity(interest1, interest2)
                
                if similarity > self.similarity_threshold:
                    self.graph.add_edge(
                        interest1['name'],
                        interest2['name'],
                        weight=similarity,
                        type='cross_interest'
                    )
    
    def _calculate_tag_similarity(self, interest: str, tags: List[str]) -> float:
        """Calculate similarity between interest and content tags"""
        if not tags:
            return 0.0
        
        # Simple word overlap similarity
        interest_words = set(interest.split())
        tag_words = set()
        for tag in tags:
            tag_words.update(tag.split())
        
        if not interest_words or not tag_words:
            return 0.0
        
        intersection = interest_words.intersection(tag_words)
        union = interest_words.union(tag_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_interest_similarity(self, interest1: Dict, interest2: Dict) -> float:
        """Calculate similarity between two interests"""
        # Use semantic similarity if embedding model is available
        if self.embedding_model:
            return self._semantic_similarity(interest1['name'], interest2['name'])
        else:
            # Fallback to simple word overlap
            return self._calculate_tag_similarity(interest1['name'], [interest2['name']])
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            self.load_embedding_model()
            
            embeddings = self.embedding_model([text1, text2])
            embedding1 = np.array(embeddings[0])
            embedding2 = np.array(embeddings[1])
            
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def find_novel_connections(self, user_interests: List[Dict], content_data: List[Dict], 
                             max_connections: int = 10) -> List[Dict[str, Any]]:
        """Find novel connections between interests"""
        # Build connection graph
        self.build_connection_graph(user_interests, content_data)
        
        # Find novel connections
        novel_connections = []
        
        # Get all interest nodes
        interest_nodes = [node for node, data in self.graph.nodes(data=True) 
                         if data.get('type') == 'interest']
        
        # Find paths between interests
        for i, interest1 in enumerate(interest_nodes):
            for interest2 in interest_nodes[i+1:]:
                # Check if there's no direct connection
                if not self.graph.has_edge(interest1, interest2):
                    # Find shortest path
                    try:
                        path = nx.shortest_path(self.graph, interest1, interest2)
                        if len(path) > 2:  # Path goes through content
                            novelty_score = self._calculate_novelty_score(path)
                            
                            if novelty_score > self.novelty_threshold:
                                connection = self._create_connection_object(path, novelty_score)
                                novel_connections.append(connection)
                    except nx.NetworkXNoPath:
                        continue
        
        # Sort by novelty score and return top connections
        novel_connections.sort(key=lambda x: x['novelty_score'], reverse=True)
        return novel_connections[:max_connections]
    
    def _calculate_novelty_score(self, path: List[str]) -> float:
        """Calculate novelty score for a connection path"""
        try:
            # Factors that increase novelty:
            # 1. Path length (longer paths are more novel)
            # 2. Diversity of content types
            # 3. Low direct similarity between endpoints
            
            path_length = len(path)
            content_diversity = self._calculate_content_diversity(path)
            
            # Calculate direct similarity between endpoints
            start_node = path[0]
            end_node = path[-1]
            direct_similarity = self._calculate_interest_similarity(
                {'name': start_node}, {'name': end_node}
            )
            
            # Novelty formula
            novelty = (path_length - 2) * 0.3 + content_diversity * 0.4 + (1 - direct_similarity) * 0.3
            
            return min(1.0, max(0.0, novelty))
            
        except Exception as e:
            print(f"Error calculating novelty score: {e}")
            return 0.0
    
    def _calculate_content_diversity(self, path: List[str]) -> float:
        """Calculate diversity of content types in path"""
        content_nodes = [node for node in path[1:-1] if node.startswith('content_')]
        
        if not content_nodes:
            return 0.0
        
        # Get content categories
        categories = set()
        for node in content_nodes:
            category = self.graph.nodes[node].get('category', 'general')
            categories.add(category)
        
        # Diversity is based on number of unique categories
        return min(1.0, len(categories) / len(content_nodes))
    
    def _create_connection_object(self, path: List[str], novelty_score: float) -> Dict[str, Any]:
        """Create a connection object from a path"""
        start_interest = path[0]
        end_interest = path[-1]
        content_nodes = [node for node in path[1:-1] if node.startswith('content_')]
        
        # Get content details
        content_details = []
        for node in content_nodes:
            node_data = self.graph.nodes[node]
            content_details.append({
                'id': node.replace('content_', ''),
                'title': node_data.get('title', ''),
                'tags': node_data.get('tags', []),
                'category': node_data.get('category', 'general')
            })
        
        return {
            'start_interest': start_interest,
            'end_interest': end_interest,
            'content_bridge': content_details,
            'novelty_score': novelty_score,
            'path_length': len(path),
            'connection_type': 'cross_domain'
        }
    
    def suggest_exploration_paths(self, user_interests: List[Dict], content_data: List[Dict],
                                exploration_level: str = 'moderate') -> List[Dict[str, Any]]:
        """Suggest exploration paths for users"""
        # Find novel connections
        novel_connections = self.find_novel_connections(user_interests, content_data)
        
        # Filter based on exploration level
        if exploration_level == 'conservative':
            threshold = 0.8
        elif exploration_level == 'moderate':
            threshold = 0.6
        elif exploration_level == 'adventurous':
            threshold = 0.4
        else:
            threshold = 0.6
        
        filtered_connections = [conn for conn in novel_connections if conn['novelty_score'] >= threshold]
        
        # Add reasoning for each connection
        for connection in filtered_connections:
            connection['reasoning'] = self._generate_connection_reasoning(connection)
            connection['exploration_value'] = self._calculate_exploration_value(connection)
        
        # Sort by exploration value
        filtered_connections.sort(key=lambda x: x['exploration_value'], reverse=True)
        
        return filtered_connections
    
    def _generate_connection_reasoning(self, connection: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for a connection"""
        start_interest = connection['start_interest']
        end_interest = connection['end_interest']
        content_bridge = connection['content_bridge']
        
        if len(content_bridge) == 1:
            content = content_bridge[0]
            return f"Your interest in '{start_interest}' connects to '{end_interest}' through content about {content.get('category', 'this topic')}."
        else:
            categories = [content.get('category', 'general') for content in content_bridge]
            unique_categories = list(set(categories))
            return f"Your interest in '{start_interest}' connects to '{end_interest}' through multiple perspectives: {', '.join(unique_categories)}."
    
    def _calculate_exploration_value(self, connection: Dict[str, Any]) -> float:
        """Calculate the exploration value of a connection"""
        # Factors that increase exploration value:
        # 1. Novelty score
        # 2. Number of content pieces in bridge
        # 3. Diversity of content categories
        # 4. Path length
        
        novelty_score = connection['novelty_score']
        content_count = len(connection['content_bridge'])
        path_length = connection['path_length']
        
        # Calculate category diversity
        categories = [content.get('category', 'general') for content in connection['content_bridge']]
        category_diversity = len(set(categories)) / max(1, len(categories))
        
        # Exploration value formula
        exploration_value = (
            novelty_score * 0.4 +
            min(1.0, content_count / 5) * 0.3 +
            category_diversity * 0.2 +
            min(1.0, (path_length - 2) / 5) * 0.1
        )
        
        return min(1.0, max(0.0, exploration_value))
    
    def generate_connection_insights(self, user_interests: List[Dict], content_data: List[Dict]) -> Dict[str, Any]:
        """Generate insights about user's interest connections"""
        self.build_connection_graph(user_interests, content_data)
        
        insights = {
            'total_interests': len(user_interests),
            'total_content': len(content_data),
            'connection_density': nx.density(self.graph),
            'interest_clusters': self._find_interest_clusters(),
            'exploration_opportunities': self._identify_exploration_opportunities(),
            'content_coverage': self._analyze_content_coverage(user_interests, content_data)
        }
        
        return insights
    
    def _find_interest_clusters(self) -> List[List[str]]:
        """Find clusters of related interests"""
        # Get only interest nodes
        interest_nodes = [node for node, data in self.graph.nodes(data=True) 
                         if data.get('type') == 'interest']
        
        # Create subgraph of interests
        interest_subgraph = self.graph.subgraph(interest_nodes)
        
        # Find connected components
        clusters = list(nx.connected_components(interest_subgraph))
        
        return [list(cluster) for cluster in clusters]
    
    def _identify_exploration_opportunities(self) -> List[Dict[str, Any]]:
        """Identify areas where user could explore new interests"""
        opportunities = []
        
        # Find interests with few connections
        interest_nodes = [node for node, data in self.graph.nodes(data=True) 
                         if data.get('type') == 'interest']
        
        for interest in interest_nodes:
            connections = list(self.graph.neighbors(interest))
            if len(connections) < 3:  # Few connections
                opportunities.append({
                    'interest': interest,
                    'connection_count': len(connections),
                    'suggestion': 'Consider exploring related topics to expand your knowledge base.'
                })
        
        return opportunities
    
    def _analyze_content_coverage(self, user_interests: List[Dict], content_data: List[Dict]) -> Dict[str, Any]:
        """Analyze how well content covers user interests"""
        coverage = {
            'well_covered_interests': [],
            'under_covered_interests': [],
            'uncovered_interests': []
        }
        
        for interest in user_interests:
            interest_name = interest['name']
            connected_content = [node for node in self.graph.neighbors(interest_name) 
                               if node.startswith('content_')]
            
            if len(connected_content) >= 5:
                coverage['well_covered_interests'].append(interest_name)
            elif len(connected_content) >= 2:
                coverage['under_covered_interests'].append(interest_name)
            else:
                coverage['uncovered_interests'].append(interest_name)
        
        return coverage
    
    def get_connection_recommendations(self, user_id: int, user_interests: List[Dict], 
                                     content_data: List[Dict], limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized connection recommendations"""
        # Find novel connections
        connections = self.find_novel_connections(user_interests, content_data, limit * 2)
        
        # Add personalized scoring
        for connection in connections:
            connection['personalized_score'] = self._calculate_personalized_score(
                connection, user_interests
            )
        
        # Sort by personalized score
        connections.sort(key=lambda x: x['personalized_score'], reverse=True)
        
        return connections[:limit]
    
    def _calculate_personalized_score(self, connection: Dict[str, Any], user_interests: List[Dict]) -> float:
        """Calculate personalized score for a connection"""
        # Factors for personalization:
        # 1. Interest weights
        # 2. User's exploration history
        # 3. Content relevance to user's interests
        
        start_interest = connection['start_interest']
        end_interest = connection['end_interest']
        
        # Get interest weights
        start_weight = next((interest.get('weight', 1.0) for interest in user_interests 
                           if interest['name'] == start_interest), 1.0)
        end_weight = next((interest.get('weight', 1.0) for interest in user_interests 
                          if interest['name'] == end_interest), 1.0)
        
        # Calculate content relevance
        content_relevance = self._calculate_content_relevance(connection['content_bridge'], user_interests)
        
        # Personalized score formula
        personalized_score = (
            start_weight * 0.3 +
            end_weight * 0.3 +
            content_relevance * 0.4
        )
        
        return min(1.0, max(0.0, personalized_score))
    
    def _calculate_content_relevance(self, content_bridge: List[Dict], user_interests: List[Dict]) -> float:
        """Calculate how relevant content bridge is to user interests"""
        if not content_bridge:
            return 0.0
        
        total_relevance = 0.0
        
        for content in content_bridge:
            content_tags = content.get('tags', [])
            max_similarity = 0.0
            
            for interest in user_interests:
                similarity = self._calculate_tag_similarity(interest['name'], content_tags)
                max_similarity = max(max_similarity, similarity)
            
            total_relevance += max_similarity
        
        return total_relevance / len(content_bridge)

# Example usage
if __name__ == "__main__":
    connection_map = CrossInterestConnectionMap()
    
    # Example user interests
    user_interests = [
        {'name': 'machine learning', 'weight': 0.9, 'category': 'technology'},
        {'name': 'climate change', 'weight': 0.7, 'category': 'environment'},
        {'name': 'philosophy', 'weight': 0.5, 'category': 'humanities'}
    ]
    
    # Example content data
    content_data = [
        {'id': 1, 'title': 'AI Ethics in Climate Solutions', 'tags': ['ai', 'ethics', 'climate'], 'category': 'technology'},
        {'id': 2, 'title': 'Philosophical Approaches to Technology', 'tags': ['philosophy', 'technology'], 'category': 'humanities'},
        {'id': 3, 'title': 'Machine Learning for Environmental Monitoring', 'tags': ['ml', 'environment'], 'category': 'technology'}
    ]
    
    # Find novel connections
    connections = connection_map.find_novel_connections(user_interests, content_data)
    
    print("Novel connections found:")
    for connection in connections:
        print(f"- {connection['start_interest']} → {connection['end_interest']} (novelty: {connection['novelty_score']:.2f})") 