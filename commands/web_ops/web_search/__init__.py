"""
Web search command for SimpleAgent.

This module provides the web_search command for searching the web and retrieving information.
"""

import json
import random
from typing import List, Dict, Any
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from commands import register_command


class UserAgentManager:
    """Manages a rotating list of user agents for web requests."""
    
    def __init__(self):
        # Chrome versions
        self.chrome_versions = ['91.0.4472.124', '92.0.4515.159', '93.0.4577.82', '94.0.4606.81', 
                              '95.0.4638.69', '96.0.4664.45', '97.0.4692.71', '98.0.4758.102']
        
        # Firefox versions
        self.firefox_versions = ['89.0', '90.0', '91.0', '92.0', '93.0', '94.0', '95.0', '96.0']
        
        # Safari versions
        self.safari_versions = ['14.0', '14.1', '15.0', '15.1', '15.2', '15.3', '15.4']
        
        # Operating systems
        self.windows_versions = ['Windows NT 10.0', 'Windows NT 11.0']
        self.mac_versions = ['Macintosh; Intel Mac OS X 10_15_7', 
                           'Macintosh; Intel Mac OS X 11_5_2',
                           'Macintosh; Intel Mac OS X 12_0_1']
        self.linux_versions = ['X11; Linux x86_64', 'X11; Ubuntu; Linux x86_64']
        
        # Mobile devices
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 14_7_1 like Mac OS X',
            'iPhone; CPU iPhone OS 15_0 like Mac OS X',
            'iPad; CPU OS 15_0 like Mac OS X',
            'Linux; Android 11; SM-G991B',
            'Linux; Android 12; Pixel 6',
            'Linux; Android 11; OnePlus 9 Pro'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/537.36'
                )
        
        # Desktop Firefox
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.firefox_versions:
                agents.append(
                    f'Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}'
                )
        
        # Desktop Safari
        for os in self.mac_versions:
            for version in self.safari_versions:
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                    f'Version/{version} Safari/605.1.15'
                )
        
        # Mobile browsers
        for device in self.mobile_devices:
            # Mobile Chrome
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/537.36'
            )
            # Mobile Safari (iOS)
            if 'iPhone' in device or 'iPad' in device:
                agents.append(
                    f'Mozilla/5.0 ({device}) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                    f'Version/{random.choice(self.safari_versions)} Mobile/15E148 Safari/604.1'
                )
        
        return agents
    
    def get_headers(self) -> Dict[str, str]:
        """Get random headers including user agent and other browser-like headers."""
        agent = random.choice(self.user_agents)
        
        # Common accept headers
        headers = {
            'User-Agent': agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        return headers


# Create a singleton instance
user_agent_manager = UserAgentManager()


def web_search(query: str, num_results: int = 5, include_snippets: bool = True) -> Dict[str, Any]:
    """
    Search the web for information.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        include_snippets: Whether to include text snippets from the pages (default: True)
        
    Returns:
        Dictionary containing search results and snippets
    """
    try:
        # Get random headers for search requests
        headers = user_agent_manager.get_headers()
        
        # Perform the search (note: googlesearch-python doesn't accept user_agent directly)
        search_results = list(search(
            query, 
            num_results=num_results,
            lang="en"
        ))
        
        results = []
        for url in search_results:
            try:
                result = {"url": url}
                
                if include_snippets:
                    # Get new random headers for each page request
                    page_headers = user_agent_manager.get_headers()
                    
                    # Fetch the page content
                    response = requests.get(url, headers=page_headers, timeout=10)
                    response.raise_for_status()
                    
                    # Parse the content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get the title
                    title = soup.title.string if soup.title else "No title"
                    result["title"] = title
                    
                    # Get a relevant snippet (first paragraph or similar)
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        # Get the first non-empty paragraph
                        for p in paragraphs:
                            text = p.get_text().strip()
                            if text and len(text) > 50:  # Ensure it's a meaningful paragraph
                                result["snippet"] = text[:500] + "..." if len(text) > 500 else text
                                break
                
                results.append(result)
                
            except Exception as e:
                # If we can't fetch a particular result, just include the URL
                results.append({
                    "url": url,
                    "error": str(e)
                })
                
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "query": query,
            "results": []
        }


# Define the schema for the web_search command
WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information about a topic",
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
                "include_snippets": {
                    "type": "boolean",
                    "description": "Whether to include text snippets from the pages (default: true)",
                    "default": True
                }
            },
            "required": ["query"]
        }
    }
}

# Register the command
register_command("web_search", web_search, WEB_SEARCH_SCHEMA) 