"""
YouTube Transcript Extraction Service
Hybrid approach using youtube-transcript-api with BeautifulSoup for metadata
Based on the approach from the video tutorial
"""
import re
import json
import requests
from typing import Optional, Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable
)
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class TranscriptService:
    """Service for extracting transcripts and metadata from YouTube videos"""
    
    def __init__(self):
        """Initialize the service with session for web scraping and YouTube API"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        # Create YouTubeTranscriptApi instance (CORRECT according to docs)
        self.ytt_api = YouTubeTranscriptApi()
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        Following the approach from the video: strip URL to get video ID
        """
        # Handle short URLs (youtu.be)
        if 'youtu.be' in url:
            match = re.search(r'youtu\.be/([0-9A-Za-z_-]{11})', url)
            if match:
                return match.group(1)
        
        # Handle standard YouTube URLs
        if 'youtube.com' in url:
            if 'v=' in url:
                match = re.search(r'v=([0-9A-Za-z_-]{11})', url)
                if match:
                    return match.group(1)
        
        # Handle embed URLs
        if 'embed/' in url:
            match = re.search(r'embed/([0-9A-Za-z_-]{11})', url)
            if match:
                return match.group(1)
        
        # If it's already just the video ID
        if re.match(r'^[0-9A-Za-z_-]{11}$', url):
            return url
            
        return None
    
    def get_video_metadata(self, video_url: str) -> Dict[str, Any]:
        """
        Use BeautifulSoup to get video title and metadata from YouTube page
        As shown in the video: use requests.get and BeautifulSoup for the title
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {video_url}")
        
        # Construct full URL
        full_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            # Get the page using requests (as shown in video)
            logger.info(f"Fetching page for video: {video_id}")
            page = self.session.get(full_url, timeout=10)
            page.raise_for_status()
            
            # Use BeautifulSoup to parse the page
            soup = BeautifulSoup(page.text, 'html.parser')
            
            # Get the title from the page (as shown in video)
            title = soup.find('title')
            video_title = title.text.replace(' - YouTube', '') if title else 'Unknown Title'
            
            # Try to get additional metadata
            metadata = {
                'video_id': video_id,
                'video_title': video_title,
                'video_url': full_url
            }
            
            # Try to extract channel name
            channel_meta = soup.find('meta', {'name': 'author'})
            if channel_meta:
                metadata['channel_name'] = channel_meta.get('content', '')
            
            # Try to extract description
            description_meta = soup.find('meta', {'name': 'description'})
            if description_meta:
                metadata['description'] = description_meta.get('content', '')[:500]  # First 500 chars
            
            # Try to extract duration from meta tags
            duration_meta = soup.find('meta', {'itemprop': 'duration'})
            if duration_meta:
                metadata['duration_iso'] = duration_meta.get('content', '')
            
            return metadata
            
        except requests.RequestException as e:
            logger.error(f"Error fetching YouTube page: {e}")
            # Return minimal metadata if page fetch fails
            return {
                'video_id': video_id,
                'video_title': 'Unknown Title',
                'video_url': full_url
            }
    
    def get_transcript_from_api(self, video_id: str, language: str = 'en') -> Optional[Dict]:
        """
        Use youtube-transcript-api to get the transcript
        Using the CORRECT API from official documentation
        """
        try:
            logger.info(f"Fetching transcript using API for video: {video_id}")
            
            # Method 1: Direct fetch with language preference
            try:
                fetched_transcript = self.ytt_api.fetch(video_id, languages=[language, 'en'])
                logger.info(f"Got transcript in {fetched_transcript.language}")
                
                # Convert to raw data format
                return {
                    'segments': fetched_transcript.to_raw_data(),
                    'language': fetched_transcript.language,
                    'is_generated': fetched_transcript.is_generated
                }
            except:
                # Try without language specification
                try:
                    fetched_transcript = self.ytt_api.fetch(video_id)
                    logger.info(f"Got transcript (auto-detected language: {fetched_transcript.language})")
                    return {
                        'segments': fetched_transcript.to_raw_data(),
                        'language': fetched_transcript.language,
                        'is_generated': fetched_transcript.is_generated
                    }
                except:
                    pass
            
            # Method 2: Use list() to find available transcripts
            try:
                transcript_list = self.ytt_api.list(video_id)
                
                # Try to find transcript in requested language
                try:
                    transcript = transcript_list.find_transcript([language])
                    fetched = transcript.fetch()
                    logger.info(f"Found transcript via list() in {language}")
                    return {
                        'segments': fetched.to_raw_data(),
                        'language': fetched.language,
                        'is_generated': fetched.is_generated
                    }
                except:
                    # Get first available transcript
                    for transcript in transcript_list:
                        try:
                            fetched = transcript.fetch()
                            logger.info(f"Got transcript in {transcript.language_code}")
                            return {
                                'segments': fetched.to_raw_data(),
                                'language': fetched.language,
                                'is_generated': fetched.is_generated
                            }
                        except:
                            continue
            except Exception as e:
                logger.warning(f"list() method failed: {e}")
                
        except NoTranscriptFound:
            logger.warning(f"No transcript found via API for video: {video_id}")
            # Try listing all transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    try:
                        data = transcript.fetch()
                        logger.info(f"Found transcript in {transcript.language_code}")
                        return {
                            'segments': data,
                            'language': transcript.language_code,
                            'is_generated': transcript.is_generated
                        }
                    except:
                        continue
            except:
                pass
                
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video: {video_id}")
        except VideoUnavailable:
            logger.error(f"Video unavailable: {video_id}")
        except Exception as e:
            logger.error(f"Error fetching transcript via API: {e}")
        
        return None
    
    def get_transcript_with_beautifulsoup_fallback(self, video_url: str) -> Optional[Dict]:
        """
        Fallback method: Try to extract transcript data from page HTML
        The video mentions this is difficult due to JavaScript, but we can try
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return None
        
        try:
            full_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(full_url, timeout=10)
            
            # Look for caption tracks in the initial player response
            # This is embedded in the page as JSON
            pattern = r'ytInitialPlayerResponse\s*=\s*({.+?})\s*;'
            match = re.search(pattern, response.text)
            
            if match:
                try:
                    player_response = json.loads(match.group(1))
                    captions = player_response.get('captions', {})
                    caption_tracks = captions.get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
                    
                    if caption_tracks:
                        # Found caption track URLs
                        for track in caption_tracks:
                            base_url = track.get('baseUrl')
                            if base_url:
                                # Fetch the captions
                                caption_response = self.session.get(base_url + '&fmt=json3', timeout=10)
                                if caption_response.status_code == 200:
                                    caption_data = caption_response.json()
                                    
                                    # Process into segments
                                    segments = []
                                    for event in caption_data.get('events', []):
                                        if 'segs' in event:
                                            text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                                            segments.append({
                                                'text': text,
                                                'start': event.get('tStartMs', 0) / 1000,
                                                'duration': event.get('dDurationMs', 0) / 1000
                                            })
                                    
                                    if segments:
                                        logger.info(f"Got transcript via BeautifulSoup fallback")
                                        return {
                                            'segments': segments,
                                            'language': track.get('languageCode', 'en'),
                                            'is_generated': track.get('kind') == 'asr'
                                        }
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.error(f"Error parsing player response: {e}")
                    
        except Exception as e:
            logger.error(f"Error in BeautifulSoup fallback: {e}")
        
        return None
    
    def get_transcript(
        self,
        video_url: str, 
        language: str = 'en',
        preserve_formatting: bool = False
    ) -> Dict[str, Any]:
        """
        Main method: Get transcript using hybrid approach
        1. Use BeautifulSoup to get video title and metadata
        2. Use youtube-transcript-api to get transcript
        3. Fall back to BeautifulSoup scraping if API fails
        """
        # Extract video ID
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {video_url}")
        
        # Step 1: Get metadata using BeautifulSoup (as shown in video)
        metadata = self.get_video_metadata(video_url)
        
        # Step 2: Try to get transcript using API (primary method from video)
        transcript_data = self.get_transcript_from_api(video_id, language)
        
        # Step 3: If API fails, try BeautifulSoup fallback
        if not transcript_data:
            logger.warning("API failed, trying BeautifulSoup fallback...")
            transcript_data = self.get_transcript_with_beautifulsoup_fallback(video_url)
        
        if not transcript_data:
            raise Exception(
                f"Could not fetch transcript using any method. "
                f"The video may not have captions enabled or they may be restricted."
            )
        
        # Process the transcript segments
        segments = transcript_data['segments']
        
        # Create full text from segments (as shown in video with output parsing)
        if preserve_formatting:
            full_text = '\n'.join([segment['text'] for segment in segments])
        else:
            # Simply join all text with spaces
            full_text = ' '.join([segment['text'] for segment in segments])
        
        # Calculate total duration
        total_duration = 0
        if segments:
            for segment in segments:
                duration = segment.get('duration', 0)
                start = segment.get('start', 0)
                end_time = start + duration
                if end_time > total_duration:
                    total_duration = end_time
        
        # Combine everything
        result = {
            'video_id': video_id,
            'video_title': metadata.get('video_title', 'Unknown Title'),
            'video_url': metadata.get('video_url', video_url),
            'channel_name': metadata.get('channel_name'),
            'description': metadata.get('description'),
            'language': transcript_data.get('language', language),
            'is_generated': transcript_data.get('is_generated', False),
            'segments': segments,
            'full_text': full_text,
            'duration': total_duration,
            'word_count': len(full_text.split())
        }
        
        logger.info(f"Successfully extracted transcript for {video_id}")
        return result
    
    @staticmethod
    def clean_transcript(text: str) -> str:
        """
        Clean transcript text for better processing
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove music/sound effect annotations
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        
        # Fix common transcript issues
        text = text.replace('\n', ' ')
        text = text.strip()
        
        return text 