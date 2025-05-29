"""Raw web read command for SimpleAgent.

This module provides the raw_web_read command for fetching the raw content of a webpage.
"""

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


def raw_web_read(
    query: str,
    num_results: int = 5,
    include_html: bool = False,
    max_length: int = 50000
) -> Dict[str, Any]:
    """
    Search and read raw content from web pages using Google Custom Search API.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        include_html: Whether to include the raw HTML (default: False)
        max_length: Maximum length of text content to return (default: 50000)
        
    Returns:
        Dictionary containing search results and raw content
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
                # Fetch the page
                response = requests.get(item["link"], timeout=15)
                response.raise_for_status()
                
                # Parse the content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Initialize result dictionary
                result = {
                    "url": item["link"],
                    "title": item.get("title", ""),
                    "status_code": response.status_code,
                    "content_type": response.headers.get('Content-Type', 'unknown')
                }
                
                # Extract all text content
                # Remove script, style, and other non-content elements
                for script in soup(["script", "style", "meta", "noscript", "svg"]):
                    script.decompose()
                    
                # Get the text content
                text_content = soup.get_text(separator="\n", strip=True)
                
                # Truncate if needed
                if len(text_content) > max_length:
                    text_content = text_content[:max_length] + "... (content truncated)"
                    result["truncated"] = True
                else:
                    result["truncated"] = False
                    
                result["text_content"] = text_content
                result["content_length"] = len(text_content)
                
                # Include raw HTML if requested
                if include_html:
                    result["html_content"] = response.text
                
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


# Define the schema for the raw_web_read command
RAW_WEB_READ_SCHEMA = {
    "type": "function",
    "function": {
        "name": "raw_web_read",
        "description": "Search and read raw content from web pages using Google Custom Search API",
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
                "include_html": {
                    "type": "boolean",
                    "description": "Whether to include the raw HTML (default: false)",
                    "default": False
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of text content to return (default: 50000)",
                    "default": 50000
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("raw_web_read", raw_web_read, RAW_WEB_READ_SCHEMA) 