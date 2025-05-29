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
        # More recent Chrome versions
        self.chrome_versions = ['108.0.5359.98', '109.0.5414.119', '110.0.5481.177', 
                              '111.0.5563.64', '112.0.5615.49', '113.0.5672.63', 
                              '114.0.5735.106', '115.0.5790.102', '116.0.5845.96',
                              '117.0.5938.62', '118.0.5993.70', '119.0.6045.105',
                              '120.0.6099.109', '121.0.6167.85']
        
        # More recent Firefox versions
        self.firefox_versions = ['102.0', '103.0', '104.0', '105.0', '106.0', '107.0',
                               '108.0', '109.0', '110.0', '111.0', '112.0', '113.0',
                               '114.0', '115.0', '116.0', '117.0', '118.0', '119.0',
                               '120.0', '121.0']
        
        # More recent Safari versions
        self.safari_versions = ['15.6.1', '16.0', '16.1', '16.2', '16.3', '16.4',
                              '16.5', '16.6', '17.0', '17.1', '17.2', '17.3']
        
        # More diverse operating systems
        self.windows_versions = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Windows NT 10.0; WOW64',
            'Windows NT 11.0; WOW64'
        ]
        
        self.mac_versions = [
            'Macintosh; Intel Mac OS X 10_15_7',
            'Macintosh; Intel Mac OS X 11_5_2',
            'Macintosh; Intel Mac OS X 12_0_1',
            'Macintosh; Intel Mac OS X 13_0_1',
            'Macintosh; Intel Mac OS X 14_0_1',
            'Macintosh; Apple M1 Mac OS X 10_15_7',
            'Macintosh; Apple M2 Mac OS X 13_0_1'
        ]
        
        self.linux_versions = [
            'X11; Linux x86_64',
            'X11; Ubuntu; Linux x86_64',
            'X11; Fedora; Linux x86_64',
            'X11; Debian; Linux x86_64',
            'X11; Linux i686',
            'X11; Linux armv7l'
        ]
        
        # More diverse mobile devices
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 15_0 like Mac OS X',
            'iPhone; CPU iPhone OS 16_0 like Mac OS X',
            'iPhone; CPU iPhone OS 17_0 like Mac OS X',
            'iPad; CPU OS 15_0 like Mac OS X',
            'iPad; CPU OS 16_0 like Mac OS X',
            'iPad; CPU OS 17_0 like Mac OS X',
            'Linux; Android 12; SM-G991B',
            'Linux; Android 13; SM-G991B',
            'Linux; Android 14; SM-G991B',
            'Linux; Android 12; Pixel 6',
            'Linux; Android 13; Pixel 6',
            'Linux; Android 14; Pixel 6',
            'Linux; Android 12; Pixel 7',
            'Linux; Android 13; Pixel 7',
            'Linux; Android 14; Pixel 7',
            'Linux; Android 12; OnePlus 9 Pro',
            'Linux; Android 13; OnePlus 9 Pro',
            'Linux; Android 14; OnePlus 9 Pro',
            'Linux; Android 12; SM-S908B',
            'Linux; Android 13; SM-S908B',
            'Linux; Android 14; SM-S908B'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        self.last_request_time = 0
        self.min_delay = 2  # Minimum delay between requests in seconds
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome with more variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                # Add some randomization to the WebKit version
                webkit_version = f"537.{random.randint(30, 40)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/{webkit_version}'
                )
        
        # Desktop Firefox with more variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.firefox_versions:
                # Add some randomization to the Gecko version
                gecko_version = f"20100101 Firefox/{version}"
                agents.append(
                    f'Mozilla/5.0 ({os}; rv:{version}) Gecko/{gecko_version}'
                )
        
        # Desktop Safari with more variations
        for os in self.mac_versions:
            for version in self.safari_versions:
                # Add some randomization to the WebKit version
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(10, 20)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{version} Safari/{webkit_version}'
                )
        
        # Mobile browsers with more variations
        for device in self.mobile_devices:
            # Mobile Chrome with variations
            webkit_version = f"537.{random.randint(30, 40)}"
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/{webkit_version}'
            )
            
            # Mobile Safari (iOS) with variations
            if 'iPhone' in device or 'iPad' in device:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(10, 20)}"
                agents.append(
                    f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{random.choice(self.safari_versions)} Mobile/15E148 Safari/{webkit_version}'
                )
        
        return agents
    
    def get_headers(self) -> Dict[str, str]:
        """Get random headers including user agent and other browser-like headers."""
        import time
        from random import uniform
        
        # Add delay between requests
        current_time = time.time()
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()
        
        agent = random.choice(self.user_agents)
        
        # More randomized headers
        accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-CA,en;q=0.9',
            'en-AU,en;q=0.9',
            'en-NZ,en;q=0.9'
        ]
        
        # Common accept headers with randomization
        headers = {
            'User-Agent': agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(random.randint(0, 1)),  # Randomize DNT
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(['document', 'empty']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store']),
            'Pragma': random.choice(['no-cache', '']),
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{random.randint(100, 120)}"',
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"'])
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