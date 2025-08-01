from typing import List, Dict, Any, Optional
import random
from collections import defaultdict

class MockConnectionMapService:
    """
    Mock connection map service for Gator
    Provides novel connections between seemingly unrelated topics without heavy dependencies
    """
    
    def __init__(self):
        self.similarity_threshold = 0.3
        self.novelty_threshold = 0.7
        self.connection_cache = {}
        
    def find_novel_connections(self, user_interests: List[Dict], content_data: List[Dict], 
                             max_connections: int = 10) -> List[Dict[str, Any]]:
        """Find novel connections between user interests"""
        connections = []
        
        # Generate mock novel connections
        for i, interest1 in enumerate(user_interests):
            for j, interest2 in enumerate(user_interests[i+1:], i+1):
                # Create a novel connection
                connection = self._create_mock_connection(interest1, interest2, content_data)
                if connection:
                    connections.append(connection)
        
        # Add some cross-domain connections
        cross_domain_connections = self._generate_cross_domain_connections(user_interests, content_data)
        connections.extend(cross_domain_connections)
        
        # Sort by novelty score and return top results
        connections.sort(key=lambda x: x.get('novelty_score', 0), reverse=True)
        return connections[:max_connections]
    
    def suggest_exploration_paths(self, user_interests: List[Dict], content_data: List[Dict],
                                exploration_level: str = 'moderate') -> List[Dict[str, Any]]:
        """Suggest exploration paths for user"""
        paths = []
        
        # Generate exploration paths based on user interests
        for interest in user_interests:
            path = self._create_exploration_path(interest, content_data, exploration_level)
            if path:
                paths.append(path)
        
        # Add some unexpected exploration paths
        unexpected_paths = self._generate_unexpected_paths(user_interests, content_data)
        paths.extend(unexpected_paths)
        
        return paths[:10]  # Return top 10 paths
    
    def _create_mock_connection(self, interest1: Dict, interest2: Dict, content_data: List[Dict]) -> Optional[Dict[str, Any]]:
        """Create a mock connection between two interests"""
        try:
            # Calculate a mock similarity score
            similarity = random.uniform(0.1, 0.9)
            
            if similarity > self.similarity_threshold:
                # Find bridging content
                bridging_content = self._find_bridging_content(interest1, interest2, content_data)
                
                connection = {
                    'interest1': interest1['name'],
                    'interest2': interest2['name'],
                    'similarity_score': similarity,
                    'novelty_score': random.uniform(0.5, 0.9),
                    'connection_type': 'cross_interest',
                    'bridging_content': bridging_content,
                    'reasoning': f"Connecting {interest1['name']} and {interest2['name']} through shared concepts",
                    'exploration_value': random.uniform(0.6, 0.9)
                }
                
                return connection
            
            return None
            
        except Exception as e:
            print(f"Error creating mock connection: {e}")
            return None
    
    def _find_bridging_content(self, interest1: Dict, interest2: Dict, content_data: List[Dict]) -> List[Dict]:
        """Find content that bridges two interests"""
        bridging_content = []
        
        # Mock bridging content
        bridge_content = {
            'id': random.randint(1000, 9999),
            'title': f"Bridging {interest1['name']} and {interest2['name']}",
            'content': f"Content that connects {interest1['name']} and {interest2['name']}",
            'tags': [interest1['name'], interest2['name'], 'bridge'],
            'category': 'cross_domain'
        }
        
        bridging_content.append(bridge_content)
        return bridging_content
    
    def _generate_cross_domain_connections(self, user_interests: List[Dict], content_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate cross-domain connections"""
        connections = []
        
        # Mock cross-domain connections
        cross_domains = [
            ('technology', 'climate change'),
            ('science', 'business'),
            ('politics', 'technology'),
            ('health', 'technology'),
            ('education', 'artificial intelligence')
        ]
        
        for domain1, domain2 in cross_domains:
            if any(interest['name'].lower() in domain1.lower() for interest in user_interests):
                connection = {
                    'interest1': domain1,
                    'interest2': domain2,
                    'similarity_score': random.uniform(0.4, 0.8),
                    'novelty_score': random.uniform(0.7, 0.9),
                    'connection_type': 'cross_domain',
                    'bridging_content': [],
                    'reasoning': f"Exploring connections between {domain1} and {domain2}",
                    'exploration_value': random.uniform(0.7, 0.9)
                }
                connections.append(connection)
        
        return connections
    
    def _create_exploration_path(self, interest: Dict, content_data: List[Dict], exploration_level: str) -> Optional[Dict[str, Any]]:
        """Create an exploration path for an interest"""
        try:
            # Generate path steps based on exploration level
            if exploration_level == 'conservative':
                steps = 2
            elif exploration_level == 'moderate':
                steps = 3
            else:  # aggressive
                steps = 4
            
            path_steps = []
            current_topic = interest['name']
            
            for i in range(steps):
                # Generate next step in the path
                next_topic = self._generate_next_topic(current_topic, i)
                path_steps.append({
                    'topic': next_topic,
                    'reasoning': f"Exploring {next_topic} as a natural progression from {current_topic}",
                    'confidence': random.uniform(0.6, 0.9)
                })
                current_topic = next_topic
            
            path = {
                'starting_interest': interest['name'],
                'path_steps': path_steps,
                'exploration_level': exploration_level,
                'total_value': random.uniform(0.5, 0.9),
                'novelty_score': random.uniform(0.4, 0.8)
            }
            
            return path
            
        except Exception as e:
            print(f"Error creating exploration path: {e}")
            return None
    
    def _generate_next_topic(self, current_topic: str, step: int) -> str:
        """Generate the next topic in an exploration path"""
        # Mock topic progression
        topic_progressions = {
            'machine learning': ['deep learning', 'neural networks', 'AI ethics'],
            'climate change': ['renewable energy', 'sustainable technology', 'green policy'],
            'artificial intelligence': ['machine learning', 'computer vision', 'AI safety'],
            'technology': ['innovation', 'startups', 'future trends'],
            'science': ['research', 'discovery', 'breakthroughs']
        }
        
        # Find progression for current topic
        for base_topic, progression in topic_progressions.items():
            if base_topic.lower() in current_topic.lower():
                if step < len(progression):
                    return progression[step]
                else:
                    return f"Advanced {base_topic}"
        
        # Default progression
        return f"Advanced {current_topic}"
    
    def _generate_unexpected_paths(self, user_interests: List[Dict], content_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate unexpected exploration paths"""
        unexpected_paths = []
        
        # Mock unexpected connections
        unexpected_connections = [
            ('technology', 'art'),
            ('science', 'philosophy'),
            ('business', 'psychology'),
            ('politics', 'psychology'),
            ('health', 'technology')
        ]
        
        for interest in user_interests:
            for domain1, domain2 in unexpected_connections:
                if domain1.lower() in interest['name'].lower():
                    path = {
                        'starting_interest': interest['name'],
                        'path_steps': [
                            {
                                'topic': domain2,
                                'reasoning': f"Unexpected connection between {domain1} and {domain2}",
                                'confidence': random.uniform(0.4, 0.7)
                            }
                        ],
                        'exploration_level': 'aggressive',
                        'total_value': random.uniform(0.6, 0.9),
                        'novelty_score': random.uniform(0.8, 0.95)
                    }
                    unexpected_paths.append(path)
        
        return unexpected_paths

# Create a singleton instance
connection_map_service = MockConnectionMapService() 