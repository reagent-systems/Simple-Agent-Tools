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
        # Chrome versions - different from others
        self.chrome_versions = ['110.0.5481.177', '111.0.5563.64', '112.0.5615.49', 
                              '113.0.5672.63', '114.0.5735.106', '115.0.5790.102', 
                              '116.0.5845.96', '117.0.5938.62', '118.0.5993.70',
                              '119.0.6045.105', '120.0.6099.109', '121.0.6167.85',
                              '122.0.6261.39', '123.0.6312.58']
        
        # Firefox versions - different from others
        self.firefox_versions = ['104.0', '105.0', '106.0', '107.0', '108.0', '109.0',
                               '110.0', '111.0', '112.0', '113.0', '114.0', '115.0',
                               '116.0', '117.0', '118.0', '119.0', '120.0', '121.0',
                               '122.0', '123.0']
        
        # Safari versions - different from others
        self.safari_versions = ['16.1', '16.2', '16.3', '16.4', '16.5', '16.6',
                              '17.0', '17.1', '17.2', '17.3', '17.4', '17.5']
        
        # Operating systems - different combinations
        self.windows_versions = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Windows NT 10.0; WOW64',
            'Windows NT 11.0; WOW64',
            'Windows NT 10.0; ARM64',
            'Windows NT 11.0; ARM64',
            'Windows NT 10.0; x64'
        ]
        
        self.mac_versions = [
            'Macintosh; Intel Mac OS X 12_0_1',
            'Macintosh; Intel Mac OS X 13_0_1',
            'Macintosh; Intel Mac OS X 14_0_1',
            'Macintosh; Apple M1 Mac OS X 12_0_1',
            'Macintosh; Apple M2 Mac OS X 13_0_1',
            'Macintosh; Apple M3 Mac OS X 14_0_1',
            'Macintosh; Apple M1 Pro Mac OS X 13_0_1'
        ]
        
        self.linux_versions = [
            'X11; Fedora; Linux x86_64',
            'X11; Debian; Linux x86_64',
            'X11; Linux i686',
            'X11; Linux armv7l',
            'X11; Linux aarch64',
            'X11; Ubuntu; Linux x86_64'
        ]
        
        # Mobile devices - different set
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 17_0 like Mac OS X',
            'iPhone; CPU iPhone OS 17_1 like Mac OS X',
            'iPhone; CPU iPhone OS 17_2 like Mac OS X',
            'iPad; CPU OS 17_0 like Mac OS X',
            'iPad; CPU OS 17_1 like Mac OS X',
            'iPad; CPU OS 17_2 like Mac OS X',
            'Linux; Android 14; SM-G991B',
            'Linux; Android 14; Pixel 6',
            'Linux; Android 14; Pixel 7',
            'Linux; Android 14; Pixel 8',
            'Linux; Android 14; OnePlus 9 Pro',
            'Linux; Android 14; SM-S908B',
            'Linux; Android 14; SM-S918B',
            'Linux; Android 14; SM-S928B'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        self.last_request_time = 0
        self.min_delay = 2.5  # Different delay for raw reading
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome with variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                webkit_version = f"537.{random.randint(40, 50)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/{webkit_version}'
                )
        
        # Desktop Firefox with variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.firefox_versions:
                gecko_version = f"20100101 Firefox/{version}"
                agents.append(
                    f'Mozilla/5.0 ({os}; rv:{version}) Gecko/{gecko_version}'
                )
        
        # Desktop Safari with variations
        for os in self.mac_versions:
            for version in self.safari_versions:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(20, 30)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{version} Safari/{webkit_version}'
                )
        
        # Mobile browsers with variations
        for device in self.mobile_devices:
            # Mobile Chrome
            webkit_version = f"537.{random.randint(40, 50)}"
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/{webkit_version}'
            )
            
            # Mobile Safari (iOS)
            if 'iPhone' in device or 'iPad' in device:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(20, 30)}"
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
            'en-CA,en;q=0.9',
            'en-AU,en;q=0.9',
            'en-NZ,en;q=0.9',
            'en-ZA,en;q=0.9',
            'en-IN,en;q=0.9'
        ]
        
        # Common accept headers with randomization
        headers = {
            'User-Agent': agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(random.randint(0, 1)),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(['document', 'empty', 'object', 'image']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors', 'websocket']),
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site', 'cross-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store', 'private', 'must-revalidate']),
            'Pragma': random.choice(['no-cache', '']),
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{random.randint(110, 130)}"',
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"']),
            'Sec-Ch-Ua-Platform-Version': f'"{random.randint(10, 14)}.0.0"'
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