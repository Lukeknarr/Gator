from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqGeneration
import torch
from typing import List, Dict, Any, Optional
import re
from nltk.tokenize import sent_tokenize
import nltk
from sqlalchemy.orm import Session
from ..models import Content, ContentSummary
from ..database import get_db
from datetime import datetime

class AISummarizationService:
    """
    AI-powered content summarization service for Gator
    Uses advanced NLP models to generate high-quality summaries
    """
    
    def __init__(self):
        self.summarizer = None
        self.extractive_summarizer = None
        self.keyword_extractor = None
        self.sentiment_analyzer = None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def load_models(self):
        """Load AI models for summarization"""
        if not self.summarizer:
            print("Loading summarization models...")
            
            # Abstractive summarization (T5-based)
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Extractive summarization
            self.extractive_summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Keyword extraction
            self.keyword_extractor = pipeline(
                "token-classification",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
    
    def summarize_content(self, content: Content, summary_type: str = "abstractive") -> Dict[str, Any]:
        """Generate summary for content"""
        try:
            self.load_models()
            
            # Prepare text for summarization
            text = self.prepare_text_for_summarization(content)
            
            if not text:
                return {"error": "No text content available"}
            
            # Generate summary based on type
            if summary_type == "abstractive":
                summary = self.generate_abstractive_summary(text)
            elif summary_type == "extractive":
                summary = self.generate_extractive_summary(text)
            elif summary_type == "hybrid":
                summary = self.generate_hybrid_summary(text)
            else:
                return {"error": "Invalid summary type"}
            
            # Extract additional insights
            insights = self.extract_content_insights(text, content)
            
            # Combine results
            result = {
                "summary": summary,
                "insights": insights,
                "content_id": content.id,
                "summary_type": summary_type
            }
            
            # Save summary to database
            self.save_summary_to_db(content.id, result)
            
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
        
        # Add content from tags (if available)
        if hasattr(content, 'tags') and content.tags:
            tag_texts = [tag.name for tag in content.tags]
            text_parts.extend(tag_texts)
        
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
    
    def generate_abstractive_summary(self, text: str, max_length: int = 150) -> str:
        """Generate abstractive summary using BART"""
        try:
            # Split text into chunks if too long
            chunks = self.split_text_into_chunks(text, max_length=1024)
            
            summaries = []
            for chunk in chunks:
                if len(chunk.split()) > 50:  # Only summarize if chunk is substantial
                    result = self.summarizer(chunk, max_length=max_length, min_length=30, do_sample=False)
                    summaries.append(result[0]['summary_text'])
            
            # Combine summaries
            if summaries:
                combined_summary = " ".join(summaries)
                # Generate final summary if combined is too long
                if len(combined_summary.split()) > max_length:
                    final_result = self.summarizer(combined_summary, max_length=max_length, min_length=30, do_sample=False)
                    return final_result[0]['summary_text']
                else:
                    return combined_summary
            else:
                return text[:max_length] + "..." if len(text) > max_length else text
                
        except Exception as e:
            print(f"Error generating abstractive summary: {e}")
            return self.generate_fallback_summary(text, max_length)
    
    def generate_extractive_summary(self, text: str, max_length: int = 150) -> str:
        """Generate extractive summary"""
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= 3:
                return text
            
            # Use extractive summarization
            result = self.extractive_summarizer(text, max_length=max_length, min_length=30, do_sample=False)
            return result[0]['summary_text']
            
        except Exception as e:
            print(f"Error generating extractive summary: {e}")
            return self.generate_fallback_summary(text, max_length)
    
    def generate_hybrid_summary(self, text: str, max_length: int = 150) -> str:
        """Generate hybrid summary combining extractive and abstractive approaches"""
        try:
            # First, generate extractive summary
            extractive_summary = self.generate_extractive_summary(text, max_length=max_length//2)
            
            # Then, generate abstractive summary from extractive summary
            if len(extractive_summary.split()) > 20:
                result = self.summarizer(extractive_summary, max_length=max_length, min_length=30, do_sample=False)
                return result[0]['summary_text']
            else:
                return extractive_summary
                
        except Exception as e:
            print(f"Error generating hybrid summary: {e}")
            return self.generate_fallback_summary(text, max_length)
    
    def generate_fallback_summary(self, text: str, max_length: int) -> str:
        """Generate fallback summary using simple text truncation"""
        sentences = sent_tokenize(text)
        
        if len(sentences) <= 2:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Take first few sentences
        summary_sentences = sentences[:3]
        summary = " ".join(summary_sentences)
        
        return summary[:max_length] + "..." if len(summary) > max_length else summary
    
    def split_text_into_chunks(self, text: str, max_length: int = 1024) -> List[str]:
        """Split text into chunks for processing"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > max_length and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def extract_content_insights(self, text: str, content: Content) -> Dict[str, Any]:
        """Extract additional insights from content"""
        insights = {}
        
        try:
            # Extract keywords
            keywords = self.extract_keywords(text)
            insights['keywords'] = keywords
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)
            insights['sentiment'] = sentiment
            
            # Extract key topics
            topics = self.extract_topics(text)
            insights['topics'] = topics
            
            # Calculate readability score
            readability = self.calculate_readability(text)
            insights['readability'] = readability
            
            # Extract key phrases
            key_phrases = self.extract_key_phrases(text)
            insights['key_phrases'] = key_phrases
            
            # Content type analysis
            content_type = self.analyze_content_type(text)
            insights['content_type'] = content_type
            
        except Exception as e:
            print(f"Error extracting insights: {e}")
            insights['error'] = str(e)
        
        return insights
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            # Use NER for keyword extraction
            entities = self.keyword_extractor(text)
            
            # Filter for relevant entities
            keywords = []
            for entity in entities:
                if entity['score'] > 0.7:  # High confidence threshold
                    keywords.append(entity['word'])
            
            # Remove duplicates and limit
            unique_keywords = list(set(keywords))
            return unique_keywords[:10]  # Top 10 keywords
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            # Split text into chunks for analysis
            sentences = sent_tokenize(text)
            
            if len(sentences) > 10:
                # Sample sentences for analysis
                sample_sentences = sentences[:10]
            else:
                sample_sentences = sentences
            
            sentiments = []
            for sentence in sample_sentences:
                if len(sentence.split()) > 3:  # Only analyze substantial sentences
                    result = self.sentiment_analyzer(sentence)
                    sentiments.append(result[0])
            
            if sentiments:
                # Calculate average sentiment
                positive_count = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
                negative_count = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
                neutral_count = sum(1 for s in sentiments if s['label'] == 'NEUTRAL')
                
                total = len(sentiments)
                return {
                    'overall_sentiment': 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'neutral',
                    'positive_ratio': positive_count / total,
                    'negative_ratio': negative_count / total,
                    'neutral_ratio': neutral_count / total,
                    'confidence': max(positive_count, negative_count, neutral_count) / total
                }
            else:
                return {'overall_sentiment': 'neutral', 'confidence': 0.0}
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'overall_sentiment': 'neutral', 'confidence': 0.0}
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
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
            print(f"Error extracting topics: {e}")
            return []
    
    def calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability metrics"""
        try:
            sentences = sent_tokenize(text)
            words = text.split()
            syllables = self.count_syllables(text)
            
            if len(sentences) == 0 or len(words) == 0:
                return {'flesch_reading_ease': 0, 'grade_level': 'Unknown'}
            
            # Flesch Reading Ease
            flesch_ease = 206.835 - (1.015 * (len(words) / len(sentences))) - (84.6 * (syllables / len(words)))
            
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
                'flesch_reading_ease': max(0, min(100, flesch_ease)),
                'grade_level': grade_level,
                'sentence_count': len(sentences),
                'word_count': len(words),
                'syllable_count': syllables
            }
            
        except Exception as e:
            print(f"Error calculating readability: {e}")
            return {'flesch_reading_ease': 0, 'grade_level': 'Unknown'}
    
    def count_syllables(self, text: str) -> int:
        """Count syllables in text (approximate)"""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return max(1, count)
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        try:
            # Extract phrases in quotes
            quoted_phrases = re.findall(r'"([^"]*)"', text)
            
            # Extract capitalized phrases
            capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            
            # Combine and limit
            phrases = quoted_phrases + capitalized_phrases[:5]
            return list(set(phrases))[:10]  # Remove duplicates and limit
            
        except Exception as e:
            print(f"Error extracting key phrases: {e}")
            return []
    
    def analyze_content_type(self, text: str) -> str:
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
    
    def save_summary_to_db(self, content_id: int, summary_data: Dict[str, Any]):
        """Save summary to database"""
        try:
            db = next(get_db())
            
            # Check if summary already exists
            existing_summary = db.query(ContentSummary).filter(
                ContentSummary.content_id == content_id
            ).first()
            
            if existing_summary:
                # Update existing summary
                existing_summary.summary_text = summary_data.get('summary', '')
                existing_summary.summary_type = summary_data.get('summary_type', 'abstractive')
                existing_summary.insights = summary_data.get('insights', {})
                existing_summary.updated_at = datetime.utcnow()
            else:
                # Create new summary
                new_summary = ContentSummary(
                    content_id=content_id,
                    summary_text=summary_data.get('summary', ''),
                    summary_type=summary_data.get('summary_type', 'abstractive'),
                    insights=summary_data.get('insights', {}),
                    created_at=datetime.utcnow()
                )
                db.add(new_summary)
            
            db.commit()
            
        except Exception as e:
            print(f"Error saving summary to database: {e}")
    
    def get_summary_for_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get existing summary for content"""
        try:
            db = next(get_db())
            
            summary = db.query(ContentSummary).filter(
                ContentSummary.content_id == content_id
            ).first()
            
            if summary:
                return {
                    'summary': summary.summary_text,
                    'summary_type': summary.summary_type,
                    'insights': summary.insights,
                    'created_at': summary.created_at.isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting summary: {e}")
            return None

# Example usage
if __name__ == "__main__":
    service = AISummarizationService()
    
    # Example content
    sample_content = Content(
        id=1,
        title="Introduction to Machine Learning",
        summary="This article provides a comprehensive overview of machine learning concepts...",
        content_type="article"
    )
    
    # Generate summary
    result = service.summarize_content(sample_content, "hybrid")
    print("Summary:", result.get('summary'))
    print("Insights:", result.get('insights')) 