"""Web scrape command for SimpleAgent.

This module provides the web_scrape command for fetching and parsing webpage content.
"""

import json
import os
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from commands import register_command


class GoogleSearchManager:
    """Manages Google Custom Search API requests."""
    
    def __init__(self):
        """Initialize the Google Search Manager with credentials from environment variables."""
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.cx = os.getenv('GOOGLE_SEARCH_CX')
        
        if not self.api_key or not self.cx:
            raise ValueError(
                "Google API credentials not found. Please set the following environment variables:\n"
                "GOOGLE_SEARCH_API_KEY: Your Google Custom Search API key\n"
                "GOOGLE_SEARCH_CX: Your Custom Search Engine ID"
            )
            
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.last_request_time = 0
        self.min_delay = 1  # Minimum delay between requests in seconds
        
    def search(
        self,
        query: str,
        num_results: int = 10,
        start_index: int = 1,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Perform a search using Google Custom Search API."""
        import time
        
        # Add delay between requests
        current_time = time.time()
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()
        
        # Prepare parameters
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': query,
            'num': min(num_results, 10),
            'start': start_index,
            'lr': f"lang_{language}",
            'safe': 'active'
        }
            
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }


def web_scrape(
    query: str,
    num_results: int = 5,
    include_content: bool = True,
    max_content_length: int = 5000
) -> Dict[str, Any]:
    """
    Search and scrape web content using Google Custom Search API.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        include_content: Whether to include the full content of pages (default: True)
        max_content_length: Maximum length of content to return (default: 5000)
        
    Returns:
        Dictionary containing search results and scraped content
    """
    try:
        # Initialize search manager
        search_manager = GoogleSearchManager()
        
        # Perform the search
        search_results = search_manager.search(
            query=query,
            num_results=num_results
        )
        
        if "error" in search_results:
            return search_results
            
        # Process results
        results = []
        for item in search_results.get("items", []):
            try:
                # Fetch the page content
                response = requests.get(item["link"], timeout=10)
                response.raise_for_status()
                
                # Parse the content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text(separator="\n", strip=True)
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)
                
                # Truncate if needed
                if len(text) > max_content_length:
                    text = text[:max_content_length] + "..."
                
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "display_url": item.get("displayLink", "")
                }
                
                if include_content:
                    result["content"] = text
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    "url": item["link"],
                    "error": str(e)
                })
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_information": search_results.get("searchInformation", {})
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "results": []
        }


# Define the schema for the web_scrape command
WEB_SCRAPE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_scrape",
        "description": "Search and scrape web content using Google Custom Search API",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5
                },
                "include_content": {
                    "type": "boolean",
                    "description": "Whether to include the full content of pages (default: true)",
                    "default": True
                },
                "max_content_length": {
                    "type": "integer",
                    "description": "Maximum length of content to return (default: 5000)",
                    "default": 5000
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("web_scrape", web_scrape, WEB_SCRAPE_SCHEMA) 