"""
Web search command for SimpleAgent.

This module provides the web_search command for searching the web using Google Custom Search API.
"""

import json
import os
import requests
from typing import Dict, Any, Optional, Tuple
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
        language: str = "en",
        date_restrict: Optional[str] = None,
        site_search: Optional[str] = None,
        site_search_filter: Optional[str] = None,
        file_type: Optional[str] = None,
        rights: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a search using Google Custom Search API.
        
        Args:
            query: The search query
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for results (for pagination)
            language: Language to search in
            date_restrict: Restrict results to a specific time period
            site_search: Site to search within
            site_search_filter: Whether to include or exclude the site
            file_type: Restrict results to specific file types
            rights: Filter by usage rights
            
        Returns:
            Dictionary containing search results
        """
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
            'num': min(num_results, 10),  # API limit is 10 per request
            'start': start_index,
            'lr': f"lang_{language}",
            'safe': 'active'
        }
        
        # Add optional parameters
        if date_restrict:
            params['dateRestrict'] = date_restrict
        if site_search:
            params['as_sitesearch'] = site_search
            if site_search_filter:
                params['as_filter'] = site_search_filter
        if file_type:
            params['fileType'] = file_type
        if rights:
            params['rights'] = rights
            
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }


def web_search(
    query: str,
    num_results: int = 5,
    language: str = "en",
    date_restrict: Optional[str] = None,
    site_search: Optional[str] = None,
    site_search_filter: Optional[str] = None,
    file_type: Optional[str] = None,
    rights: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search the web using Google Custom Search API.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        language: Language to search in (default: en)
        date_restrict: Restrict results to a specific time period
        site_search: Site to search within
        site_search_filter: Whether to include or exclude the site
        file_type: Restrict results to specific file types
        rights: Filter by usage rights
        
    Returns:
        Dictionary containing search results
    """
    try:
        # Initialize search manager
        search_manager = GoogleSearchManager()
        
        # Calculate number of requests needed
        total_results = []
        remaining_results = num_results
        start_index = 1
        
        while remaining_results > 0 and len(total_results) < num_results:
            # Get results for this page
            results = search_manager.search(
                query=query,
                num_results=min(remaining_results, 10),
                start_index=start_index,
                language=language,
                date_restrict=date_restrict,
                site_search=site_search,
                site_search_filter=site_search_filter,
                file_type=file_type,
                rights=rights
            )
            
            if "error" in results:
                return results
                
            # Process results
            if "items" in results:
                for item in results["items"]:
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "display_url": item.get("displayLink", ""),
                        "file_type": item.get("fileFormat", ""),
                        "mime_type": item.get("mime", ""),
                        "image": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", ""),
                        "metatags": item.get("pagemap", {}).get("metatags", [{}])[0]
                    }
                    total_results.append(result)
                    
                    if len(total_results) >= num_results:
                        break
            
            # Update for next iteration
            remaining_results -= len(results.get("items", []))
            start_index += len(results.get("items", []))
            
            # Check if we've reached the end
            if "queries" in results and "nextPage" not in results["queries"]:
                break
        
        return {
            "query": query,
            "results": total_results,
            "total_results": len(total_results),
            "search_information": results.get("searchInformation", {})
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "results": []
        }


# Define the schema for the web_search command
WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web using Google Custom Search API",
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
                "language": {
                    "type": "string",
                    "description": "Language to search in (default: en)",
                    "default": "en"
                },
                "date_restrict": {
                    "type": "string",
                    "description": "Restrict results to a specific time period (e.g., 'd[number]' for days, 'w[number]' for weeks, 'm[number]' for months, 'y[number]' for years)"
                },
                "site_search": {
                    "type": "string",
                    "description": "Site to search within"
                },
                "site_search_filter": {
                    "type": "string",
                    "description": "Whether to include or exclude the site (i: include, e: exclude)",
                    "enum": ["i", "e"]
                },
                "file_type": {
                    "type": "string",
                    "description": "Restrict results to specific file types (e.g., 'pdf', 'doc', 'xls')"
                },
                "rights": {
                    "type": "string",
                    "description": "Filter by usage rights (e.g., 'cc_publicdomain', 'cc_attribute', 'cc_sharealike')"
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("web_search", web_search, WEB_SEARCH_SCHEMA) 