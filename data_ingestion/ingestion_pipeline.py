import feedparser
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import spacy
from transformers import pipeline
import re
from typing import List, Dict, Any, Optional
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import backend models
import sys
sys.path.append('../backend')
from backend.models import Content, Tag, Base
from backend.database import engine, SessionLocal

class ContentIngestionPipeline:
    def __init__(self):
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize topic classification
        self.topic_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Database session
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # RSS feeds to monitor
        self.rss_feeds = [
            "https://feeds.feedburner.com/TechCrunch",
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://feeds.npr.org/1001/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        ]
        
        # Substack newsletters
        self.substack_feeds = [
            "https://stratechery.com/feed/",
            "https://www.theinformation.com/feed",
            "https://www.axios.com/feed"
        ]
        
        # Arxiv categories
        self.arxiv_categories = [
            "cs.AI", "cs.LG", "cs.CV", "cs.NE", "cs.CL",
            "physics.soc-ph", "econ.EM", "stat.ML"
        ]
    
    def run_pipeline(self):
        """Run the complete ingestion pipeline"""
        print("Starting content ingestion pipeline...")
        
        # Ingest from different sources
        self.ingest_rss_feeds()
        self.ingest_substack_feeds()
        self.ingest_arxiv_papers()
        
        print("Content ingestion pipeline completed!")
    
    def ingest_rss_feeds(self):
        """Ingest content from RSS feeds"""
        print("Ingesting RSS feeds...")
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                    content_data = self._parse_rss_entry(entry, feed_url)
                    if content_data:
                        self._save_content(content_data)
                        
            except Exception as e:
                print(f"Error ingesting RSS feed {feed_url}: {e}")
    
    def ingest_substack_feeds(self):
        """Ingest content from Substack newsletters"""
        print("Ingesting Substack feeds...")
        
        for feed_url in self.substack_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Limit to 5 entries per feed
                    content_data = self._parse_substack_entry(entry, feed_url)
                    if content_data:
                        self._save_content(content_data)
                        
            except Exception as e:
                print(f"Error ingesting Substack feed {feed_url}: {e}")
    
    def ingest_arxiv_papers(self):
        """Ingest papers from Arxiv"""
        print("Ingesting Arxiv papers...")
        
        for category in self.arxiv_categories:
            try:
                feed_url = f"http://export.arxiv.org/rss/{category}"
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Limit to 5 papers per category
                    content_data = self._parse_arxiv_entry(entry, category)
                    if content_data:
                        self._save_content(content_data)
                        
            except Exception as e:
                print(f"Error ingesting Arxiv category {category}: {e}")
    
    def _parse_rss_entry(self, entry, feed_url: str) -> Optional[Dict[str, Any]]:
        """Parse RSS entry into content data"""
        try:
            # Extract title and link
            title = entry.get('title', '')
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            # Extract summary
            summary = entry.get('summary', '')
            if not summary:
                summary = entry.get('description', '')
            
            # Extract author
            author = entry.get('author', 'Unknown')
            
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed'):
                published_at = datetime(*entry.published_parsed[:6])
            
            # Determine source
            source = self._extract_source_from_url(feed_url)
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'author': author,
                'published_at': published_at,
                'source': source,
                'content_type': 'article'
            }
            
        except Exception as e:
            print(f"Error parsing RSS entry: {e}")
            return None
    
    def _parse_substack_entry(self, entry, feed_url: str) -> Optional[Dict[str, Any]]:
        """Parse Substack entry into content data"""
        try:
            title = entry.get('title', '')
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            summary = entry.get('summary', '')
            author = entry.get('author', 'Unknown')
            
            published_at = None
            if hasattr(entry, 'published_parsed'):
                published_at = datetime(*entry.published_parsed[:6])
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'author': author,
                'published_at': published_at,
                'source': 'substack',
                'content_type': 'article'
            }
            
        except Exception as e:
            print(f"Error parsing Substack entry: {e}")
            return None
    
    def _parse_arxiv_entry(self, entry, category: str) -> Optional[Dict[str, Any]]:
        """Parse Arxiv entry into content data"""
        try:
            title = entry.get('title', '')
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            summary = entry.get('summary', '')
            
            # Extract authors from title (Arxiv format: "Title" by Author1, Author2
            author = "Unknown"
            if " by " in title:
                title_parts = title.split(" by ")
                title = title_parts[0].strip('"')
                author = title_parts[1]
            
            published_at = None
            if hasattr(entry, 'published_parsed'):
                published_at = datetime(*entry.published_parsed[:6])
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'author': author,
                'published_at': published_at,
                'source': 'arxiv',
                'content_type': 'paper'
            }
            
        except Exception as e:
            print(f"Error parsing Arxiv entry: {e}")
            return None
    
    def _extract_source_from_url(self, feed_url: str) -> str:
        """Extract source name from feed URL"""
        if 'techcrunch' in feed_url:
            return 'techcrunch'
        elif 'cnn' in feed_url:
            return 'cnn'
        elif 'bbc' in feed_url:
            return 'bbc'
        elif 'npr' in feed_url:
            return 'npr'
        elif 'nytimes' in feed_url:
            return 'nytimes'
        else:
            return 'rss'
    
    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """Extract tags using NLP"""
        tags = []
        
        # Combine title and summary for analysis
        text = f"{title} {summary}"
        
        # Use spaCy for named entity recognition
        doc = self.nlp(text)
        
        # Extract named entities as potential tags
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']:
                tags.append(ent.text.lower())
        
        # Use topic classification
        candidate_topics = [
            "technology", "politics", "science", "business", "health",
            "entertainment", "sports", "education", "environment", "finance"
        ]
        
        try:
            result = self.topic_classifier(text, candidate_topics)
            if result['scores'][0] > 0.5:  # Confidence threshold
                tags.append(result['labels'][0])
        except Exception as e:
            print(f"Topic classification error: {e}")
        
        # Extract common keywords
        keywords = self._extract_keywords(text)
        tags.extend(keywords)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common words and extract potential keywords
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Clean text
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # Filter out common words and short words
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        
        # Return top keywords (limit to 5)
        return keywords[:5]
    
    def _save_content(self, content_data: Dict[str, Any]):
        """Save content to database"""
        db = self.SessionLocal()
        try:
            # Check if content already exists
            existing_content = db.query(Content).filter(Content.url == content_data['url']).first()
            if existing_content:
                return  # Skip if already exists
            
            # Create content
            content = Content(
                title=content_data['title'],
                url=content_data['url'],
                source=content_data['source'],
                author=content_data['author'],
                published_at=content_data['published_at'],
                summary=content_data['summary'],
                content_type=content_data['content_type']
            )
            
            db.add(content)
            db.commit()
            db.refresh(content)
            
            # Extract and add tags
            tags = self._extract_tags(content_data['title'], content_data['summary'])
            for tag_name in tags:
                # Get or create tag
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, category='topic')
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                
                # Add tag to content
                content.tags.append(tag)
            
            db.commit()
            print(f"Saved content: {content_data['title']}")
            
        except Exception as e:
            print(f"Error saving content: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    pipeline = ContentIngestionPipeline()
    pipeline.run_pipeline()
