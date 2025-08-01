from typing import List, Dict, Any, Optional
import re
from sqlalchemy.orm import Session
from models import Content
from database import get_db
from datetime import datetime

class AISummarizationService:
    """
    Mock AI-powered content summarization service for Gator
    Uses simple text processing for deployment compatibility
    """
    
    def __init__(self):
        self.summarizer = "mock"
        self.extractive_summarizer = "mock"
        self.keyword_extractor = "mock"
        self.sentiment_analyzer = "mock"
    
    def load_models(self):
        """Load mock models for summarization"""
        print("Using mock summarization service")
    
    def summarize_content(self, content: Content, summary_type: str = "abstractive") -> Dict[str, Any]:
        """Generate mock summary for content"""
        try:
            # Prepare text for summarization
            text = self.prepare_text_for_summarization(content)
            
            if not text:
                return {"error": "No text content available"}
            
            # Generate mock summary
            summary = self.generate_mock_summary(text, summary_type)
            
            # Extract mock insights
            insights = self.extract_mock_insights(text, content)
            
            # Combine results
            result = {
                "summary": summary,
                "insights": insights,
                "content_id": content.id,
                "summary_type": summary_type
            }
            
            return result
            
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return {"error": str(e)}
    
    def prepare_text_for_summarization(self, content: Content) -> str:
        """Prepare text content for summarization"""
        text_parts = []
        
        # Add title
        if content.title:
            text_parts.append(content.title)
        
        # Add summary if available
        if content.summary:
            text_parts.append(content.summary)
        
        # Combine all text
        full_text = " ".join(text_parts)
        
        # Clean and preprocess text
        cleaned_text = self.clean_text(full_text)
        
        return cleaned_text
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:]', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        return text.strip()
    
    def generate_mock_summary(self, text: str, summary_type: str = "abstractive", max_length: int = 150) -> str:
        """Generate mock summary using simple text processing"""
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return self.generate_fallback_summary(text, max_length)
            
            # Take first few sentences as summary
            summary_sentences = sentences[:3]
            summary = ". ".join(summary_sentences)
            
            # Truncate if too long
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            print(f"Error generating mock summary: {e}")
            return self.generate_fallback_summary(text, max_length)
    
    def generate_fallback_summary(self, text: str, max_length: int) -> str:
        """Generate fallback summary using simple text truncation"""
        if len(text) <= max_length:
            return text
        
        # Take first part of text
        summary = text[:max_length-3] + "..."
        return summary
    
    def extract_mock_insights(self, text: str, content: Content) -> Dict[str, Any]:
        """Extract mock insights from content"""
        insights = {}
        
        try:
            # Extract mock keywords
            keywords = self.extract_mock_keywords(text)
            insights['keywords'] = keywords
            
            # Analyze mock sentiment
            sentiment = self.analyze_mock_sentiment(text)
            insights['sentiment'] = sentiment
            
            # Extract mock topics
            topics = self.extract_mock_topics(text)
            insights['topics'] = topics
            
            # Calculate mock readability score
            readability = self.calculate_mock_readability(text)
            insights['readability'] = readability
            
            # Extract mock key phrases
            key_phrases = self.extract_mock_key_phrases(text)
            insights['key_phrases'] = key_phrases
            
            # Content type analysis
            content_type = self.analyze_mock_content_type(text)
            insights['content_type'] = content_type
            
        except Exception as e:
            print(f"Error extracting mock insights: {e}")
            insights['error'] = str(e)
        
        return insights
    
    def extract_mock_keywords(self, text: str) -> List[str]:
        """Extract mock keywords from text"""
        try:
            # Simple keyword extraction based on word frequency
            words = text.lower().split()
            word_freq = {}
            
            # Common words to exclude
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            for word in words:
                if len(word) > 3 and word not in common_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10]]
            
        except Exception as e:
            print(f"Error extracting mock keywords: {e}")
            return []
    
    def analyze_mock_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze mock sentiment"""
        try:
            # Simple sentiment analysis based on positive/negative words
            positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like'}
            negative_words = {'bad', 'terrible', 'awful', 'hate', 'dislike', 'poor', 'worst'}
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_words = len(words)
            if total_words == 0:
                return {"sentiment": "neutral", "confidence": 0.0}
            
            polarity = (positive_count - negative_count) / total_words
            confidence = abs(polarity)
            
            if polarity > 0.01:
                sentiment = "positive"
            elif polarity < -0.01:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "polarity": polarity,
                "subjectivity": 0.5,  # Mock value
                "sentiment": sentiment,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error analyzing mock sentiment: {e}")
            return {
                "polarity": 0.0,
                "subjectivity": 0.5,
                "sentiment": "neutral",
                "confidence": 0.0
            }
    
    def extract_mock_topics(self, text: str) -> List[str]:
        """Extract mock topics from text"""
        try:
            # Simple topic extraction based on frequency
            words = text.lower().split()
            word_freq = {}
            
            # Common words to exclude
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            for word in words:
                if len(word) > 3 and word not in common_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top topics
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:5]]
            
        except Exception as e:
            print(f"Error extracting mock topics: {e}")
            return []
    
    def calculate_mock_readability(self, text: str) -> Dict[str, Any]:
        """Calculate mock readability metrics"""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            words = text.split()
            
            if len(sentences) == 0 or len(words) == 0:
                return {'flesch_reading_ease': 0, 'grade_level': 'Unknown'}
            
            # Mock Flesch Reading Ease calculation
            avg_sentence_length = len(words) / len(sentences)
            flesch_ease = max(0, min(100, 100 - avg_sentence_length * 2))
            
            # Determine grade level
            if flesch_ease >= 90:
                grade_level = "5th grade"
            elif flesch_ease >= 80:
                grade_level = "6th grade"
            elif flesch_ease >= 70:
                grade_level = "7th grade"
            elif flesch_ease >= 60:
                grade_level = "8th-9th grade"
            elif flesch_ease >= 50:
                grade_level = "10th-12th grade"
            elif flesch_ease >= 30:
                grade_level = "College"
            else:
                grade_level = "College graduate"
            
            return {
                'flesch_reading_ease': flesch_ease,
                'grade_level': grade_level,
                'sentence_count': len(sentences),
                'word_count': len(words)
            }
            
        except Exception as e:
            print(f"Error calculating mock readability: {e}")
            return {'flesch_reading_ease': 0, 'grade_level': 'Unknown'}
    
    def extract_mock_key_phrases(self, text: str) -> List[str]:
        """Extract mock key phrases from text"""
        try:
            # Extract phrases in quotes
            quoted_phrases = re.findall(r'"([^"]*)"', text)
            
            # Extract capitalized phrases
            capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            
            # Combine and limit
            phrases = quoted_phrases + capitalized_phrases[:5]
            return list(set(phrases))[:10]  # Remove duplicates and limit
            
        except Exception as e:
            print(f"Error extracting mock key phrases: {e}")
            return []
    
    def analyze_mock_content_type(self, text: str) -> str:
        """Analyze the type of content"""
        text_lower = text.lower()
        
        # Check for technical content
        technical_indicators = ['algorithm', 'code', 'programming', 'software', 'technology', 'api', 'database']
        if any(indicator in text_lower for indicator in technical_indicators):
            return 'technical'
        
        # Check for news content
        news_indicators = ['breaking', 'news', 'announcement', 'update', 'reported', 'according']
        if any(indicator in text_lower for indicator in news_indicators):
            return 'news'
        
        # Check for educational content
        educational_indicators = ['learn', 'education', 'tutorial', 'guide', 'how to', 'explain']
        if any(indicator in text_lower for indicator in educational_indicators):
            return 'educational'
        
        # Check for opinion content
        opinion_indicators = ['opinion', 'think', 'believe', 'feel', 'argue', 'suggest']
        if any(indicator in text_lower for indicator in opinion_indicators):
            return 'opinion'
        
        return 'general'
    
    def get_summary_for_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get existing summary for content"""
        try:
            # Mock implementation - return None for now
            return None
            
        except Exception as e:
            print(f"Error getting summary: {e}")
            return None 