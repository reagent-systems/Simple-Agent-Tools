"""
YouTube Video Info command for SimpleAgent.

This module provides the youtube_info command for extracting video information from YouTube URLs.
"""

import re
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from commands import register_command


class YouTubeInfoManager:
    """Manages extracting information from YouTube videos."""
    
    def __init__(self):
        """Initialize the YouTube Info Manager."""
        # Using yt-dlp style extraction with requests and regex
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID if found, None otherwise
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get video information using YouTube's oEmbed API and web scraping.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video information
        """
        try:
            # Use YouTube oEmbed API for basic info
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            
            response = self.session.get(oembed_url, timeout=30)
            
            if response.status_code == 200:
                oembed_data = response.json()
                
                # Get additional info by scraping the watch page
                watch_url = f"https://www.youtube.com/watch?v={video_id}"
                watch_response = self.session.get(watch_url, timeout=30)
                
                additional_info = {}
                if watch_response.status_code == 200:
                    additional_info = self._extract_from_watch_page(watch_response.text)
                
                # Combine data
                video_info = {
                    "video_id": video_id,
                    "title": oembed_data.get("title", ""),
                    "author_name": oembed_data.get("author_name", ""),
                    "author_url": oembed_data.get("author_url", ""),
                    "thumbnail_url": oembed_data.get("thumbnail_url", ""),
                    "html": oembed_data.get("html", ""),
                    "width": oembed_data.get("width", 0),
                    "height": oembed_data.get("height", 0),
                    "provider_name": oembed_data.get("provider_name", "YouTube"),
                    "provider_url": oembed_data.get("provider_url", "https://www.youtube.com/"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    **additional_info
                }
                
                return {
                    "success": True,
                    "video_info": video_info
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch video info: HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _extract_from_watch_page(self, html_content: str) -> Dict[str, Any]:
        """
        Extract additional information from YouTube watch page HTML.
        
        Args:
            html_content: HTML content of the watch page
            
        Returns:
            Dictionary with extracted information
        """
        additional_info = {}
        
        try:
            # Extract description
            desc_pattern = r'"shortDescription":"([^"]*)"'
            desc_match = re.search(desc_pattern, html_content)
            if desc_match:
                description = desc_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                additional_info["description"] = description[:1000] + "..." if len(description) > 1000 else description
            
            # Extract view count
            views_pattern = r'"viewCount":"(\d+)"'
            views_match = re.search(views_pattern, html_content)
            if views_match:
                additional_info["view_count"] = int(views_match.group(1))
            
            # Extract duration
            duration_pattern = r'"lengthSeconds":"(\d+)"'
            duration_match = re.search(duration_pattern, html_content)
            if duration_match:
                duration_seconds = int(duration_match.group(1))
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                additional_info["duration"] = f"{minutes}:{seconds:02d}"
                additional_info["duration_seconds"] = duration_seconds
            
            # Extract upload date
            upload_pattern = r'"uploadDate":"([^"]*)"'
            upload_match = re.search(upload_pattern, html_content)
            if upload_match:
                additional_info["upload_date"] = upload_match.group(1)
            
            # Extract like count (may not always be available)
            likes_pattern = r'"accessibilityText":"([^"]*likes[^"]*)"'
            likes_match = re.search(likes_pattern, html_content)
            if likes_match:
                likes_text = likes_match.group(1)
                additional_info["likes_info"] = likes_text
            
        except Exception:
            # If extraction fails, just return what we have
            pass
        
        return additional_info


def youtube_info(url: str) -> Dict[str, Any]:
    """
    Extract information from a YouTube video URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing video information including title, description, duration, view count, etc.
    """
    try:
        if not url or not url.strip():
            return {
                "success": False,
                "error": "URL cannot be empty"
            }
        
        # Initialize YouTube info manager
        manager = YouTubeInfoManager()
        
        # Extract video ID
        video_id = manager.extract_video_id(url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL or unable to extract video ID"
            }
        
        # Get video information
        return manager.get_video_info(video_id)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


# Define the schema for the youtube_info command
YOUTUBE_INFO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "youtube_info",
        "description": "Extract information from a YouTube video including title, description, duration, view count, and metadata",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "YouTube video URL (supports various formats: youtube.com/watch?v=, youtu.be/, etc.)"
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("youtube_info", youtube_info, YOUTUBE_INFO_SCHEMA) 