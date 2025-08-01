import yt_dlp
import whisper
import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs

class MultiModalIngestionPipeline:
    """
    Multi-modal content ingestion pipeline for Gator
    Supports video transcripts, podcasts, and other media types
    """
    
    def __init__(self):
        self.whisper_model = None
        self.supported_video_platforms = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'ted.com'
        ]
        self.supported_podcast_platforms = [
            'spotify.com', 'apple.co', 'podcasts.apple.com', 'anchor.fm'
        ]
        
    def load_whisper_model(self):
        """Load Whisper model for transcription"""
        if not self.whisper_model:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def ingest_video_content(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Ingest video content and extract transcript"""
        try:
            # Check if URL is supported
            if not any(platform in video_url for platform in self.supported_video_platforms):
                print(f"Unsupported video platform: {video_url}")
                return None
            
            # Download video and extract transcript
            transcript = self.extract_video_transcript(video_url)
            if not transcript:
                return None
            
            # Extract metadata
            metadata = self.extract_video_metadata(video_url)
            
            # Process transcript for content analysis
            processed_content = self.process_transcript(transcript, metadata)
            
            return {
                'url': video_url,
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'duration': metadata.get('duration', 0),
                'transcript': transcript,
                'processed_content': processed_content,
                'source': 'video',
                'content_type': 'video',
                'published_at': metadata.get('published_at'),
                'tags': processed_content.get('tags', [])
            }
            
        except Exception as e:
            print(f"Error ingesting video content: {e}")
            return None
    
    def extract_video_transcript(self, video_url: str) -> Optional[str]:
        """Extract transcript from video using yt-dlp and Whisper"""
        try:
            # Configure yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'temp/%(id)s.%(ext)s'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info
                info = ydl.extract_info(video_url, download=False)
                video_id = info.get('id')
                
                # Check if transcript is available
                if info.get('subtitles') or info.get('automatic_captions'):
                    # Use available subtitles
                    subtitles = info.get('subtitles', {})
                    auto_captions = info.get('automatic_captions', {})
                    
                    # Prefer manual subtitles over automatic captions
                    if subtitles:
                        for lang, subs in subtitles.items():
                            if lang.startswith('en'):
                                for sub in subs:
                                    if sub.get('ext') == 'vtt':
                                        subtitle_url = sub['url']
                                        transcript = self.download_subtitle(subtitle_url)
                                        if transcript:
                                            return transcript
                    
                    # Fallback to automatic captions
                    if auto_captions:
                        for lang, subs in auto_captions.items():
                            if lang.startswith('en'):
                                for sub in subs:
                                    if sub.get('ext') == 'vtt':
                                        subtitle_url = sub['url']
                                        transcript = self.download_subtitle(subtitle_url)
                                        if transcript:
                                            return transcript
                
                # If no subtitles available, download audio and transcribe
                print("No subtitles available, downloading audio for transcription...")
                ydl.download([video_url])
                
                # Transcribe audio using Whisper
                audio_file = f"temp/{video_id}.mp3"
                if os.path.exists(audio_file):
                    model = self.load_whisper_model()
                    result = model.transcribe(audio_file)
                    
                    # Clean up audio file
                    os.remove(audio_file)
                    
                    return result['text']
            
            return None
            
        except Exception as e:
            print(f"Error extracting video transcript: {e}")
            return None
    
    def download_subtitle(self, subtitle_url: str) -> Optional[str]:
        """Download and parse subtitle file"""
        try:
            response = requests.get(subtitle_url)
            if response.status_code == 200:
                # Parse VTT format
                vtt_content = response.text
                transcript = self.parse_vtt(vtt_content)
                return transcript
            return None
        except Exception as e:
            print(f"Error downloading subtitle: {e}")
            return None
    
    def parse_vtt(self, vtt_content: str) -> str:
        """Parse VTT subtitle format"""
        lines = vtt_content.split('\n')
        transcript_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip timestamp lines and empty lines
            if (line and 
                not line.startswith('-->') and 
                not re.match(r'^\d+:\d+:\d+', line) and
                not line.startswith('WEBVTT')):
                transcript_lines.append(line)
        
        return ' '.join(transcript_lines)
    
    def extract_video_metadata(self, video_url: str) -> Dict[str, Any]:
        """Extract metadata from video URL"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    'title': info.get('title', ''),
                    'author': info.get('uploader', ''),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'published_at': info.get('upload_date'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0)
                }
        except Exception as e:
            print(f"Error extracting video metadata: {e}")
            return {}
    
    def ingest_podcast_content(self, podcast_url: str) -> Optional[Dict[str, Any]]:
        """Ingest podcast content and extract transcript"""
        try:
            # Check if URL is supported
            if not any(platform in podcast_url for platform in self.supported_podcast_platforms):
                print(f"Unsupported podcast platform: {podcast_url}")
                return None
            
            # Extract podcast metadata
            metadata = self.extract_podcast_metadata(podcast_url)
            if not metadata:
                return None
            
            # Try to get transcript
            transcript = self.get_podcast_transcript(podcast_url, metadata)
            
            # Process content
            processed_content = self.process_transcript(transcript, metadata) if transcript else {}
            
            return {
                'url': podcast_url,
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'duration': metadata.get('duration', 0),
                'transcript': transcript,
                'processed_content': processed_content,
                'source': 'podcast',
                'content_type': 'podcast',
                'published_at': metadata.get('published_at'),
                'tags': processed_content.get('tags', [])
            }
            
        except Exception as e:
            print(f"Error ingesting podcast content: {e}")
            return None
    
    def extract_podcast_metadata(self, podcast_url: str) -> Optional[Dict[str, Any]]:
        """Extract podcast metadata from various platforms"""
        try:
            parsed_url = urlparse(podcast_url)
            
            if 'spotify.com' in podcast_url:
                return self.extract_spotify_metadata(podcast_url)
            elif 'apple.co' in podcast_url or 'podcasts.apple.com' in podcast_url:
                return self.extract_apple_podcast_metadata(podcast_url)
            elif 'anchor.fm' in podcast_url:
                return self.extract_anchor_metadata(podcast_url)
            else:
                # Generic metadata extraction
                return self.extract_generic_metadata(podcast_url)
                
        except Exception as e:
            print(f"Error extracting podcast metadata: {e}")
            return None
    
    def extract_spotify_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Spotify podcast URLs"""
        # This would require Spotify API integration
        # For now, return basic metadata
        return {
            'title': 'Spotify Podcast',
            'author': 'Unknown',
            'duration': 0,
            'description': '',
            'tags': ['podcast', 'spotify']
        }
    
    def extract_apple_podcast_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Apple Podcast URLs"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.find('h1')
                author = soup.find('a', {'class': 'link'})
                description = soup.find('p', {'class': 'description'})
                
                return {
                    'title': title.text.strip() if title else 'Apple Podcast',
                    'author': author.text.strip() if author else 'Unknown',
                    'duration': 0,
                    'description': description.text.strip() if description else '',
                    'tags': ['podcast', 'apple']
                }
        except Exception as e:
            print(f"Error extracting Apple podcast metadata: {e}")
        
        return {
            'title': 'Apple Podcast',
            'author': 'Unknown',
            'duration': 0,
            'description': '',
            'tags': ['podcast', 'apple']
        }
    
    def extract_anchor_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Anchor.fm URLs"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.find('title')
                description = soup.find('meta', {'name': 'description'})
                
                return {
                    'title': title.text.strip() if title else 'Anchor Podcast',
                    'author': 'Unknown',
                    'duration': 0,
                    'description': description.get('content', '') if description else '',
                    'tags': ['podcast', 'anchor']
                }
        except Exception as e:
            print(f"Error extracting Anchor metadata: {e}")
        
        return {
            'title': 'Anchor Podcast',
            'author': 'Unknown',
            'duration': 0,
            'description': '',
            'tags': ['podcast', 'anchor']
        }
    
    def extract_generic_metadata(self, url: str) -> Dict[str, Any]:
        """Extract generic metadata from any URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.find('title')
                description = soup.find('meta', {'name': 'description'})
                
                return {
                    'title': title.text.strip() if title else 'Unknown Content',
                    'author': 'Unknown',
                    'duration': 0,
                    'description': description.get('content', '') if description else '',
                    'tags': ['podcast', 'generic']
                }
        except Exception as e:
            print(f"Error extracting generic metadata: {e}")
        
        return {
            'title': 'Unknown Content',
            'author': 'Unknown',
            'duration': 0,
            'description': '',
            'tags': ['podcast', 'generic']
        }
    
    def get_podcast_transcript(self, url: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Get transcript for podcast (if available)"""
        # Most podcasts don't have easily accessible transcripts
        # This would require integration with services like:
        # - Spotify's transcript API
        # - Apple Podcasts transcript API
        # - Third-party transcript services
        
        # For now, return None
        return None
    
    def process_transcript(self, transcript: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process transcript for content analysis"""
        if not transcript:
            return {}
        
        # Extract key topics and themes
        topics = self.extract_topics(transcript)
        
        # Generate summary
        summary = self.generate_summary(transcript)
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(transcript)
        
        return {
            'topics': topics,
            'summary': summary,
            'key_phrases': key_phrases,
            'tags': topics + key_phrases
        }
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        # Simple topic extraction based on frequency
        words = text.lower().split()
        word_freq = {}
        
        # Count word frequency (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        for word in words:
            if len(word) > 3 and word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 most frequent words as topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def generate_summary(self, text: str) -> str:
        """Generate a summary of the transcript"""
        # Simple summary: first few sentences
        sentences = text.split('.')
        summary_sentences = sentences[:3]  # First 3 sentences
        return '. '.join(summary_sentences) + '.'
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple key phrase extraction
        # This could be enhanced with NLP libraries
        phrases = []
        
        # Extract phrases in quotes
        quoted_phrases = re.findall(r'"([^"]*)"', text)
        phrases.extend(quoted_phrases)
        
        # Extract capitalized phrases (potential proper nouns)
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        phrases.extend(capitalized_phrases[:5])  # Limit to 5
        
        return list(set(phrases))  # Remove duplicates
    
    def run_pipeline(self, urls: List[str]):
        """Run the multi-modal ingestion pipeline"""
        print("Starting multi-modal content ingestion...")
        
        for url in urls:
            print(f"Processing: {url}")
            
            # Determine content type and process accordingly
            if any(platform in url for platform in self.supported_video_platforms):
                content = self.ingest_video_content(url)
            elif any(platform in url for platform in self.supported_podcast_platforms):
                content = self.ingest_podcast_content(url)
            else:
                print(f"Unsupported content type: {url}")
                continue
            
            if content:
                # Save to database (integrate with existing pipeline)
                self.save_content(content)
                print(f"Successfully processed: {content['title']}")
            else:
                print(f"Failed to process: {url}")
        
        print("Multi-modal ingestion completed!")

# Example usage
if __name__ == "__main__":
    pipeline = MultiModalIngestionPipeline()
    
    # Example URLs
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Video
        "https://podcasts.apple.com/us/podcast/example",  # Podcast
    ]
    
    pipeline.run_pipeline(urls) 