"""Raw web read command for SimpleAgent.

This module provides the raw_web_read command for fetching the raw content of a webpage.
"""

import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
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


def raw_web_read(url: str, include_html: bool = False, max_length: int = 50000) -> Dict[str, Any]:
    """
    Fetch the raw content of a webpage with minimal processing.
    
    Args:
        url: The URL to read
        include_html: Whether to include the raw HTML in the response (default: False)
        max_length: Maximum length of text content to return (default: 50000)
        
    Returns:
        Dictionary containing the raw webpage content
    """
    try:
        # Get random headers for this request
        headers = user_agent_manager.get_headers()
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize result dictionary
        result = {
            "url": url,
            "title": soup.title.string if soup.title else None,
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
            html_content = response.text
            if len(html_content) > max_length:
                html_content = html_content[:max_length] + "... (HTML truncated)"
                result["html_truncated"] = True
            else:
                result["html_truncated"] = False
                
            result["html_content"] = html_content
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to read webpage: {str(e)}",
            "url": url
        }


# Define the schema for the raw_web_read command
RAW_WEB_READ_SCHEMA = {
    "type": "function",
    "function": {
        "name": "raw_web_read",
        "description": "Fetch the raw content of a webpage with minimal processing",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to read"
                },
                "include_html": {
                    "type": "boolean",
                    "description": "Whether to include the raw HTML in the response (default: false)",
                    "default": False
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of text content to return (default: 50000)",
                    "default": 50000
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("raw_web_read", raw_web_read, RAW_WEB_READ_SCHEMA) 