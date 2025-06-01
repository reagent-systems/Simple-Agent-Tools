"""
Social Media Scraper command for SimpleAgent.

This module provides the social_scrape command for extracting content from social media platforms (Twitter/Reddit).
"""

import re
import requests
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, quote
from commands import register_command


class SocialMediaScraper:
    """Manages scraping content from various social media platforms."""
    
    def __init__(self):
        """Initialize the Social Media Scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_twitter_post(self, url: str) -> Dict[str, Any]:
        """
        Scrape a Twitter post using public methods.
        
        Args:
            url: Twitter post URL
            
        Returns:
            Dictionary containing post information
        """
        try:
            # Extract tweet ID from URL
            tweet_id_match = re.search(r'/status/(\d+)', url)
            if not tweet_id_match:
                return {
                    "success": False,
                    "error": "Invalid Twitter URL - could not extract tweet ID"
                }
            
            tweet_id = tweet_id_match.group(1)
            
            # Use Twitter's oEmbed API for basic info
            oembed_url = f"https://publish.twitter.com/oembed?url={quote(url)}"
            
            response = self.session.get(oembed_url, timeout=30)
            
            if response.status_code == 200:
                oembed_data = response.json()
                
                # Extract text from HTML
                html_content = oembed_data.get('html', '')
                
                # Parse the HTML to extract text
                text_content = self._extract_text_from_html(html_content)
                
                return {
                    "success": True,
                    "platform": "twitter",
                    "post_id": tweet_id,
                    "author": oembed_data.get('author_name', ''),
                    "author_url": oembed_data.get('author_url', ''),
                    "text": text_content,
                    "html": html_content,
                    "url": url,
                    "width": oembed_data.get('width', 0),
                    "height": oembed_data.get('height', 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch Twitter post: HTTP {response.status_code}"
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
    
    def scrape_reddit_post(self, url: str) -> Dict[str, Any]:
        """
        Scrape a Reddit post using Reddit's JSON API.
        
        Args:
            url: Reddit post URL
            
        Returns:
            Dictionary containing post information
        """
        try:
            # Convert Reddit URL to JSON format
            if not url.endswith('.json'):
                json_url = url.rstrip('/') + '.json'
            else:
                json_url = url
            
            response = self.session.get(json_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Reddit returns an array with post data and comments
                if isinstance(data, list) and len(data) > 0:
                    post_data = data[0]['data']['children'][0]['data']
                    
                    # Extract comments if available
                    comments = []
                    if len(data) > 1 and 'data' in data[1]:
                        comments_data = data[1]['data']['children']
                        for comment in comments_data[:5]:  # Get top 5 comments
                            if comment['kind'] == 't1' and 'body' in comment['data']:
                                comments.append({
                                    'author': comment['data'].get('author', '[deleted]'),
                                    'body': comment['data']['body'][:500],  # Limit comment length
                                    'score': comment['data'].get('score', 0),
                                    'created_utc': comment['data'].get('created_utc', 0)
                                })
                    
                    return {
                        "success": True,
                        "platform": "reddit",
                        "post_id": post_data.get('id', ''),
                        "title": post_data.get('title', ''),
                        "author": post_data.get('author', ''),
                        "subreddit": post_data.get('subreddit', ''),
                        "text": post_data.get('selftext', ''),
                        "url": post_data.get('url', ''),
                        "score": post_data.get('score', 0),
                        "num_comments": post_data.get('num_comments', 0),
                        "created_utc": post_data.get('created_utc', 0),
                        "upvote_ratio": post_data.get('upvote_ratio', 0),
                        "is_video": post_data.get('is_video', False),
                        "comments": comments,
                        "permalink": f"https://reddit.com{post_data.get('permalink', '')}"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid Reddit response format"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch Reddit post: HTTP {response.status_code}"
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
    
    def scrape_reddit_trending(self, subreddit: str = "popular", limit: int = 10) -> Dict[str, Any]:
        """
        Get trending posts from a Reddit subreddit.
        
        Args:
            subreddit: Subreddit name (default: "popular")
            limit: Number of posts to retrieve (max 25)
            
        Returns:
            Dictionary containing trending posts
        """
        try:
            limit = min(limit, 25)  # Reddit API limit
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                posts = []
                if 'data' in data and 'children' in data['data']:
                    for post in data['data']['children']:
                        post_data = post['data']
                        posts.append({
                            'title': post_data.get('title', ''),
                            'author': post_data.get('author', ''),
                            'subreddit': post_data.get('subreddit', ''),
                            'score': post_data.get('score', 0),
                            'num_comments': post_data.get('num_comments', 0),
                            'url': post_data.get('url', ''),
                            'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                            'created_utc': post_data.get('created_utc', 0),
                            'upvote_ratio': post_data.get('upvote_ratio', 0),
                            'selftext': post_data.get('selftext', '')[:200]  # Limit text preview
                        })
                
                return {
                    "success": True,
                    "platform": "reddit",
                    "subreddit": subreddit,
                    "posts": posts,
                    "count": len(posts)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch Reddit trending: HTTP {response.status_code}"
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
    
    def _extract_text_from_html(self, html: str) -> str:
        """
        Extract text content from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        # Remove HTML tags and extract text
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def detect_platform(self, url: str) -> str:
        """
        Detect social media platform from URL.
        
        Args:
            url: Social media URL
            
        Returns:
            Platform name or 'unknown'
        """
        url_lower = url.lower()
        if 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'reddit.com' in url_lower:
            return 'reddit'
        else:
            return 'unknown'


def social_scrape(
    url: Optional[str] = None,
    platform: Optional[str] = None,
    action: str = "post",
    subreddit: str = "popular",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Scrape content from social media platforms.
    
    Args:
        url: Social media post URL (required for 'post' action)
        platform: Platform name (twitter, reddit) - auto-detected if not specified
        action: Action to perform ('post' to scrape specific post, 'trending' for trending content)
        subreddit: Subreddit name for Reddit trending (default: "popular")
        limit: Number of posts to retrieve for trending (max 25)
        
    Returns:
        Dictionary containing scraped content
    """
    try:
        scraper = SocialMediaScraper()
        
        if action == "post":
            if not url:
                return {
                    "success": False,
                    "error": "URL is required for post scraping"
                }
            
            # Detect platform if not specified
            if not platform:
                platform = scraper.detect_platform(url)
            
            if platform == "twitter":
                return scraper.scrape_twitter_post(url)
            elif platform == "reddit":
                return scraper.scrape_reddit_post(url)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}. Use 'twitter' or 'reddit'"
                }
        
        elif action == "trending":
            if platform == "reddit" or not platform:
                return scraper.scrape_reddit_trending(subreddit, limit)
            else:
                return {
                    "success": False,
                    "error": "Trending is currently only supported for Reddit"
                }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported action: {action}. Use 'post' or 'trending'"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


# Define the schema for the social_scrape command
SOCIAL_SCRAPE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "social_scrape",
        "description": "Scrape content from social media platforms (Twitter/Reddit) including posts and trending topics",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Social media post URL (required for 'post' action)"
                },
                "platform": {
                    "type": "string",
                    "description": "Platform name (twitter, reddit) - auto-detected if not specified",
                    "enum": ["twitter", "reddit"]
                },
                "action": {
                    "type": "string",
                    "description": "Action to perform",
                    "enum": ["post", "trending"],
                    "default": "post"
                },
                "subreddit": {
                    "type": "string",
                    "description": "Subreddit name for Reddit trending (default: 'popular')",
                    "default": "popular"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of posts to retrieve for trending (max 25)",
                    "minimum": 1,
                    "maximum": 25,
                    "default": 10
                }
            },
            "required": []
        }
    }
}

# Register the command
register_command("social_scrape", social_scrape, SOCIAL_SCRAPE_SCHEMA) 