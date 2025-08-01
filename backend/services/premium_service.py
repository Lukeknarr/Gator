import requests
from bs4 import BeautifulSoup
import scholarly
import arxiv
import feedparser
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from sqlalchemy.orm import Session
from ..models import Content, User, PremiumSubscription
from ..database import get_db

class PremiumService:
    """
    Premium service for Gator providing advanced features:
    - Deeper web scraping
    - Academic paper access
    - Curated expert lists
    - Advanced analytics
    """
    
    def __init__(self):
        self.scraping_delay = 1  # Delay between requests
        self.max_depth = 3  # Maximum scraping depth
        self.academic_sources = [
            'arxiv.org', 'scholar.google.com', 'researchgate.net',
            'academia.edu', 'semanticscholar.org', 'pubmed.ncbi.nlm.nih.gov'
        ]
        self.expert_curators = {
            'technology': ['tech_expert_1', 'tech_expert_2'],
            'science': ['science_expert_1', 'science_expert_2'],
            'business': ['business_expert_1', 'business_expert_2'],
            'politics': ['politics_expert_1', 'politics_expert_2']
        }
    
    def check_premium_access(self, user_id: int) -> bool:
        """Check if user has premium access"""
        try:
            db = next(get_db())
            subscription = db.query(PremiumSubscription).filter(
                PremiumSubscription.user_id == user_id,
                PremiumSubscription.is_active == True
            ).first()
            
            return subscription is not None
            
        except Exception as e:
            print(f"Error checking premium access: {e}")
            return False
    
    def deep_web_scraping(self, url: str, depth: int = 2) -> List[Dict[str, Any]]:
        """Perform deep web scraping with premium features"""
        scraped_content = []
        visited_urls = set()
        
        def scrape_page(current_url: str, current_depth: int):
            if current_depth > depth or current_url in visited_urls:
                return
            
            visited_urls.add(current_url)
            
            try:
                # Add delay to be respectful
                time.sleep(self.scraping_delay)
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(current_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract content
                    content = self._extract_page_content(soup, current_url)
                    if content:
                        scraped_content.append(content)
                    
                    # Find links for deeper scraping
                    if current_depth < depth:
                        links = self._extract_links(soup, current_url)
                        for link in links[:5]:  # Limit to 5 links per page
                            scrape_page(link, current_depth + 1)
                            
            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
        
        # Start scraping
        scrape_page(url, 0)
        return scraped_content
    
    def _extract_page_content(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a web page"""
        try:
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            # Extract main content
            main_content = ''
            
            # Try different selectors for main content
            content_selectors = [
                'article', 'main', '.content', '.post', '.entry',
                '[role="main"]', '.article-content', '.post-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text().strip()
                    break
            
            # Fallback to body content
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text().strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract keywords
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            keywords = meta_keywords.get('content', '').split(',') if meta_keywords else []
            
            # Extract author
            author = ''
            author_selectors = [
                '.author', '.byline', '[rel="author"]', '.post-author'
            ]
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text().strip()
                    break
            
            # Extract publication date
            date = ''
            date_selectors = [
                'time', '.date', '.published', '.post-date'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get_text().strip()
                    break
            
            if title_text and main_content:
                return {
                    'url': url,
                    'title': title_text,
                    'content': main_content,
                    'description': description,
                    'keywords': keywords,
                    'author': author,
                    'date': date,
                    'scraped_at': datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from a page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                continue
            
            # Only include links from the same domain
            if urlparse(href).netloc == base_domain:
                links.append(href)
        
        return list(set(links))  # Remove duplicates
    
    def search_academic_papers(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search academic papers using multiple sources"""
        papers = []
        
        # Search arXiv
        arxiv_papers = self._search_arxiv(query, max_results // 2)
        papers.extend(arxiv_papers)
        
        # Search Google Scholar
        scholar_papers = self._search_google_scholar(query, max_results // 2)
        papers.extend(scholar_papers)
        
        # Remove duplicates and sort by relevance
        unique_papers = self._deduplicate_papers(papers)
        return unique_papers[:max_results]
    
    def _search_arxiv(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search arXiv for papers"""
        papers = []
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for result in search.results():
                paper = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'summary': result.summary,
                    'url': result.entry_id,
                    'pdf_url': result.pdf_url,
                    'published_date': result.published.isoformat(),
                    'source': 'arxiv',
                    'categories': result.categories
                }
                papers.append(paper)
                
        except Exception as e:
            print(f"Error searching arXiv: {e}")
        
        return papers
    
    def _search_google_scholar(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Google Scholar for papers"""
        papers = []
        
        try:
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                paper = {
                    'title': result.get('title', ''),
                    'authors': result.get('author', []),
                    'summary': result.get('bib', {}).get('abstract', ''),
                    'url': result.get('pub_url', ''),
                    'citations': result.get('num_citations', 0),
                    'source': 'google_scholar',
                    'year': result.get('bib', {}).get('year', '')
                }
                papers.append(paper)
                
        except Exception as e:
            print(f"Error searching Google Scholar: {e}")
        
        return papers
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity"""
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            title = paper.get('title', '').lower()
            
            # Check if similar title already exists
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = self._calculate_title_similarity(title, seen_title)
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_papers.append(paper)
                seen_titles.add(title)
        
        return unique_papers
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_curated_expert_lists(self, category: str = None) -> List[Dict[str, Any]]:
        """Get curated expert lists for different categories"""
        experts = []
        
        if category:
            categories = [category]
        else:
            categories = list(self.expert_curators.keys())
        
        for cat in categories:
            if cat in self.expert_curators:
                expert_ids = self.expert_curators[cat]
                
                for expert_id in expert_ids:
                    expert = self._get_expert_details(expert_id, cat)
                    if expert:
                        experts.append(expert)
        
        return experts
    
    def _get_expert_details(self, expert_id: str, category: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific expert"""
        # This would typically fetch from a database
        # For now, return mock data
        expert_data = {
            'tech_expert_1': {
                'name': 'Dr. Sarah Chen',
                'title': 'AI Research Scientist',
                'organization': 'Stanford University',
                'expertise': ['machine learning', 'artificial intelligence', 'computer vision'],
                'bio': 'Leading researcher in AI and machine learning with 15+ years of experience.',
                'publications': 45,
                'citations': 1200,
                'category': 'technology'
            },
            'science_expert_1': {
                'name': 'Dr. Michael Rodriguez',
                'title': 'Climate Scientist',
                'organization': 'MIT',
                'expertise': ['climate change', 'atmospheric science', 'environmental modeling'],
                'bio': 'Expert in climate modeling and environmental science.',
                'publications': 32,
                'citations': 890,
                'category': 'science'
            },
            'business_expert_1': {
                'name': 'Dr. Emily Watson',
                'title': 'Strategy Professor',
                'organization': 'Harvard Business School',
                'expertise': ['business strategy', 'innovation', 'startups'],
                'bio': 'Leading expert in business strategy and innovation.',
                'publications': 28,
                'citations': 650,
                'category': 'business'
            }
        }
        
        return expert_data.get(expert_id)
    
    def get_expert_recommendations(self, user_interests: List[Dict]) -> List[Dict[str, Any]]:
        """Get personalized expert recommendations based on user interests"""
        recommendations = []
        
        # Get all experts
        all_experts = self.get_curated_expert_lists()
        
        # Score experts based on user interests
        for expert in all_experts:
            score = self._calculate_expert_relevance(expert, user_interests)
            if score > 0.3:  # Only recommend if relevance > 30%
                expert['relevance_score'] = score
                recommendations.append(expert)
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations[:10]  # Top 10 experts
    
    def _calculate_expert_relevance(self, expert: Dict[str, Any], user_interests: List[Dict]) -> float:
        """Calculate relevance of expert to user interests"""
        expert_expertise = set(expert.get('expertise', []))
        
        total_score = 0.0
        total_weight = 0.0
        
        for interest in user_interests:
            interest_name = interest['name'].lower()
            weight = interest.get('weight', 1.0)
            
            # Calculate overlap with expert expertise
            max_similarity = 0.0
            for expertise in expert_expertise:
                similarity = self._calculate_title_similarity(interest_name, expertise.lower())
                max_similarity = max(max_similarity, similarity)
            
            total_score += max_similarity * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def get_premium_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get premium analytics for user"""
        try:
            db = next(get_db())
            
            # Get user's content consumption
            user_content = db.query(Content).filter(
                Content.user_id == user_id
            ).all()
            
            # Calculate analytics
            analytics = {
                'total_content_consumed': len(user_content),
                'content_by_category': self._analyze_content_by_category(user_content),
                'reading_patterns': self._analyze_reading_patterns(user_content),
                'interest_evolution': self._analyze_interest_evolution(user_id),
                'exploration_score': self._calculate_exploration_score(user_content),
                'knowledge_gaps': self._identify_knowledge_gaps(user_id)
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting premium analytics: {e}")
            return {}
    
    def _analyze_content_by_category(self, content_list: List[Content]) -> Dict[str, int]:
        """Analyze content consumption by category"""
        categories = {}
        
        for content in content_list:
            category = getattr(content, 'category', 'general')
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _analyze_reading_patterns(self, content_list: List[Content]) -> Dict[str, Any]:
        """Analyze user's reading patterns"""
        if not content_list:
            return {}
        
        # Analyze reading times
        reading_times = []
        for content in content_list:
            if hasattr(content, 'reading_time') and content.reading_time:
                reading_times.append(content.reading_time)
        
        patterns = {
            'average_reading_time': sum(reading_times) / len(reading_times) if reading_times else 0,
            'total_reading_time': sum(reading_times),
            'content_count': len(content_list),
            'preferred_content_types': self._get_preferred_content_types(content_list)
        }
        
        return patterns
    
    def _get_preferred_content_types(self, content_list: List[Content]) -> List[str]:
        """Get user's preferred content types"""
        type_counts = {}
        
        for content in content_list:
            content_type = getattr(content, 'content_type', 'article')
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        # Sort by count and return top types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [content_type for content_type, count in sorted_types[:3]]
    
    def _analyze_interest_evolution(self, user_id: int) -> List[Dict[str, Any]]:
        """Analyze how user's interests have evolved over time"""
        # This would analyze historical interest data
        # For now, return mock data
        return [
            {
                'period': '2024-Q1',
                'interests': ['technology', 'ai'],
                'new_interests': ['machine learning']
            },
            {
                'period': '2024-Q2',
                'interests': ['technology', 'ai', 'machine learning'],
                'new_interests': ['climate change']
            }
        ]
    
    def _calculate_exploration_score(self, content_list: List[Content]) -> float:
        """Calculate user's exploration score"""
        if not content_list:
            return 0.0
        
        # Calculate diversity of content consumed
        categories = set()
        for content in content_list:
            category = getattr(content, 'category', 'general')
            categories.add(category)
        
        # Exploration score based on category diversity
        exploration_score = min(1.0, len(categories) / 10.0)  # Normalize to 0-1
        
        return exploration_score
    
    def _identify_knowledge_gaps(self, user_id: int) -> List[Dict[str, Any]]:
        """Identify potential knowledge gaps for the user"""
        # This would analyze user's interests vs available content
        # For now, return mock data
        return [
            {
                'area': 'Advanced Machine Learning',
                'reason': 'You show interest in AI but haven\'t explored advanced ML topics',
                'suggested_content': ['Deep Learning Fundamentals', 'Neural Network Architectures']
            },
            {
                'area': 'Climate Science',
                'reason': 'You read about technology but haven\'t explored climate-related tech',
                'suggested_content': ['Green Technology', 'Sustainable AI']
            }
        ]
    
    def get_premium_recommendations(self, user_id: int, user_interests: List[Dict]) -> List[Dict[str, Any]]:
        """Get premium recommendations combining multiple sources"""
        recommendations = []
        
        # Get academic paper recommendations
        for interest in user_interests[:3]:  # Top 3 interests
            papers = self.search_academic_papers(interest['name'], 5)
            for paper in papers:
                paper['source'] = 'academic'
                paper['interest'] = interest['name']
                recommendations.append(paper)
        
        # Get expert recommendations
        experts = self.get_expert_recommendations(user_interests)
        for expert in experts:
            expert['source'] = 'expert'
            recommendations.append(expert)
        
        # Get deep-scraped content recommendations
        # This would be based on user's reading history
        # For now, return academic and expert recommendations
        
        return recommendations[:20]  # Top 20 premium recommendations

# Example usage
if __name__ == "__main__":
    premium_service = PremiumService()
    
    # Example user interests
    user_interests = [
        {'name': 'machine learning', 'weight': 0.9},
        {'name': 'climate change', 'weight': 0.7}
    ]
    
    # Get premium recommendations
    recommendations = premium_service.get_premium_recommendations(1, user_interests)
    
    print("Premium recommendations:")
    for rec in recommendations[:5]:
        print(f"- {rec.get('title', rec.get('name', 'Unknown'))} ({rec.get('source', 'unknown')})") 