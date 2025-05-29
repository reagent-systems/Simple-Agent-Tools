"""Extract links command for SimpleAgent.

This module provides the extract_links command for fetching and categorizing links from web pages.
"""

import os
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
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


def extract_links(
    query: str,
    num_results: int = 5,
    max_links_per_page: int = 50,
    categorize: bool = True
) -> Dict[str, Any]:
    """
    Search web pages and extract links using Google Custom Search API.
    
    Args:
        query: The search query
        num_results: Number of search results to process (default: 5)
        max_links_per_page: Maximum number of links to extract per page (default: 50)
        categorize: Whether to categorize the links (default: True)
        
    Returns:
        Dictionary containing search results and extracted links
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
                    "links": []
                }
                
                # Extract all links
                links = []
                for a in soup.find_all('a', href=True):
                    href = a.get('href')
                    if href:
                        # Make relative URLs absolute
                        absolute_url = urljoin(item["link"], href)
                        parsed_url = urlparse(absolute_url)
                        
                        # Skip javascript: and mailto: links
                        if parsed_url.scheme in ['http', 'https']:
                            link_info = {
                                "url": absolute_url,
                                "text": a.get_text(strip=True),
                                "title": a.get('title', '')
                            }
                            
                            if categorize:
                                # Categorize the link
                                if parsed_url.netloc == urlparse(item["link"]).netloc:
                                    link_info["type"] = "internal"
                                else:
                                    link_info["type"] = "external"
                                    
                                # Add file type if present
                                path = parsed_url.path.lower()
                                if path.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                                    link_info["file_type"] = path.split('.')[-1]
                            
                            links.append(link_info)
                            
                            if len(links) >= max_links_per_page:
                                break
                
                result["links"] = links
                result["total_links"] = len(links)
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


# Define the schema for the extract_links command
EXTRACT_LINKS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "extract_links",
        "description": "Search web pages and extract links using Google Custom Search API",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to process (default: 5)",
                    "default": 5
                },
                "max_links_per_page": {
                    "type": "integer",
                    "description": "Maximum number of links to extract per page (default: 50)",
                    "default": 50
                },
                "categorize": {
                    "type": "boolean",
                    "description": "Whether to categorize the links (default: true)",
                    "default": True
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("extract_links", extract_links, EXTRACT_LINKS_SCHEMA) 