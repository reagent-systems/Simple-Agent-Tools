"""
Fetch JSON API command for SimpleAgent.

This module provides the fetch_json_api command for fetching and parsing JSON data from web APIs.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
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


def fetch_json_api(
    query: str,
    num_results: int = 5,
    timeout: int = 30,
    verify_ssl: bool = True
) -> Dict[str, Any]:
    """
    Search and fetch JSON data from web APIs using Google Custom Search API.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certificates (default: True)
        
    Returns:
        Dictionary containing search results and JSON data
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
                # Fetch the API response
                response = requests.get(
                    item["link"],
                    timeout=timeout,
                    verify=verify_ssl,
                    headers={
                        'Accept': 'application/json',
                        'User-Agent': 'SimpleAgent/1.0'
                    }
                )
                response.raise_for_status()
                
                # Try to parse JSON
                try:
                    json_data = response.json()
                    result = {
                        "url": item["link"],
                        "title": item.get("title", ""),
                        "status_code": response.status_code,
                        "content_type": response.headers.get('Content-Type', 'unknown'),
                        "data": json_data
                    }
                except json.JSONDecodeError:
                    result = {
                        "url": item["link"],
                        "error": "Response is not valid JSON",
                        "content_type": response.headers.get('Content-Type', 'unknown'),
                        "raw_content": response.text[:1000] + "..." if len(response.text) > 1000 else response.text
                    }
                
                results.append(result)
                
            except requests.exceptions.RequestException as e:
                results.append({
                    "url": item["link"],
                    "error": str(e),
                    "status_code": getattr(e.response, 'status_code', None)
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


# Define the schema for the fetch_json_api command
FETCH_JSON_API_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_json_api",
        "description": "Search and fetch JSON data from web APIs using Google Custom Search API",
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
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds (default: 30)",
                    "default": 30
                },
                "verify_ssl": {
                    "type": "boolean",
                    "description": "Whether to verify SSL certificates (default: true)",
                    "default": True
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("fetch_json_api", fetch_json_api, FETCH_JSON_API_SCHEMA) 