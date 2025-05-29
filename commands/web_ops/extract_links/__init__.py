"""Extract links command for SimpleAgent.

This module provides the extract_links command for fetching and categorizing links from a webpage.
"""

import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse
from commands import register_command


class UserAgentManager:
    """Manages a rotating list of user agents for web requests."""
    
    def __init__(self):
        # Chrome versions - different from others
        self.chrome_versions = ['121.0.6167.85', '122.0.6261.39', '123.0.6312.58', 
                              '124.0.6367.79', '125.0.6422.60', '126.0.6478.40',
                              '127.0.6533.40', '128.0.6587.40', '129.0.6637.40']
        
        # Firefox versions - different from others
        self.firefox_versions = ['121.0', '122.0', '123.0', '124.0', '125.0', '126.0',
                               '127.0', '128.0', '129.0', '130.0', '131.0']
        
        # Safari versions - different from others
        self.safari_versions = ['17.1', '17.2', '17.3', '17.4', '17.5', '17.6',
                              '17.7', '18.0', '18.1', '18.2', '18.3']
        
        # Operating systems - different combinations
        self.windows_versions = [
            'Windows NT 11.0; Win64; x64',
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; ARM64',
            'Windows NT 10.0; ARM64',
            'Windows NT 11.0; x64',
            'Windows NT 10.0; x64',
            'Windows NT 11.0; Win64; x64; rv:120.0'
        ]
        
        self.mac_versions = [
            'Macintosh; Apple M3 Mac OS X 14_0_1',
            'Macintosh; Apple M2 Mac OS X 14_0_1',
            'Macintosh; Apple M1 Mac OS X 14_0_1',
            'Macintosh; Apple M3 Pro Mac OS X 14_0_1',
            'Macintosh; Apple M2 Pro Mac OS X 14_0_1',
            'Macintosh; Apple M1 Pro Mac OS X 14_0_1',
            'Macintosh; Apple M3 Max Mac OS X 14_0_1'
        ]
        
        self.linux_versions = [
            'X11; Linux aarch64',
            'X11; Linux x86_64',
            'X11; Ubuntu; Linux x86_64',
            'X11; Fedora; Linux x86_64',
            'X11; Debian; Linux x86_64',
            'X11; Linux i686'
        ]
        
        # Mobile devices - different set
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 17_4 like Mac OS X',
            'iPhone; CPU iPhone OS 18_0 like Mac OS X',
            'iPhone; CPU iPhone OS 18_1 like Mac OS X',
            'iPad; CPU OS 17_4 like Mac OS X',
            'iPad; CPU OS 18_0 like Mac OS X',
            'iPad; CPU OS 18_1 like Mac OS X',
            'Linux; Android 14; Pixel 8 Pro',
            'Linux; Android 14; SM-S928B',
            'Linux; Android 14; SM-S918B',
            'Linux; Android 14; OnePlus 12',
            'Linux; Android 14; SM-S928U'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        self.last_request_time = 0
        self.min_delay = 2.0  # Different delay for link extraction
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome with variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                webkit_version = f"537.{random.randint(60, 70)}"
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
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(40, 50)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{version} Safari/{webkit_version}'
                )
        
        # Mobile browsers with variations
        for device in self.mobile_devices:
            # Mobile Chrome
            webkit_version = f"537.{random.randint(60, 70)}"
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/{webkit_version}'
            )
            
            # Mobile Safari (iOS)
            if 'iPhone' in device or 'iPad' in device:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(40, 50)}"
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
            'en-GB,en;q=0.9',
            'en-CA,en;q=0.9',
            'en-AU,en;q=0.9',
            'en-NZ,en;q=0.9',
            'en-ZA,en;q=0.9'
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
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{random.randint(125, 145)}"',
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"']),
            'Sec-Ch-Ua-Platform-Version': f'"{random.randint(10, 14)}.0.0"',
            'Sec-Ch-Ua-Full-Version': f'"{random.randint(125, 145)}.0.0.0"',
            'Referer': 'https://www.google.com/'
        }
        
        return headers


# Create a singleton instance
user_agent_manager = UserAgentManager()


def extract_links(url: str, categorize: bool = True, follow_redirects: bool = False) -> Dict[str, Any]:
    """
    Extract all links from a webpage with optional categorization.
    
    Args:
        url: The URL to extract links from
        categorize: Whether to categorize links by type (default: True)
        follow_redirects: Whether to follow redirects when categorizing external links (default: False)
        
    Returns:
        Dictionary containing the extracted links
    """
    try:
        # Get random headers for this request
        headers = user_agent_manager.get_headers()
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract base URL components for relative link resolution
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        base_scheme = parsed_url.scheme
        base_url = f"{base_scheme}://{base_domain}"
        
        # Find all links in the page
        all_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                # Create the full URL if it's a relative link
                full_url = urljoin(url, href)
                
                # Get link text and title
                link_text = link.get_text(strip=True) or "[No Text]"
                link_title = link.get('title', '')
                
                all_links.append({
                    "url": full_url,
                    "text": link_text[:100] + ("..." if len(link_text) > 100 else ""),
                    "title": link_title,
                    "is_relative": not bool(urlparse(href).netloc)
                })
        
        result = {
            "url": url,
            "title": soup.title.string if soup.title else None,
            "total_links": len(all_links),
            "links": all_links
        }
        
        # Categorize links if requested
        if categorize:
            internal_links = []
            external_links = []
            media_links = []
            document_links = []
            
            # Media and document extensions
            media_exts = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.mp4', '.webm', '.avi', '.mov']
            doc_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.zip', '.rar']
            
            for link in all_links:
                link_url = link["url"]
                parsed_link = urlparse(link_url)
                
                # Check if link is internal or external
                if parsed_link.netloc == base_domain or not parsed_link.netloc:
                    internal_links.append(link)
                else:
                    # If we need to follow redirects to check final URL
                    if follow_redirects:
                        try:
                            head_response = requests.head(link_url, headers=headers, timeout=5, allow_redirects=True)
                            link["final_url"] = head_response.url
                            link["status_code"] = head_response.status_code
                        except Exception:
                            # If we can't follow the redirect, just use the original URL
                            link["final_url"] = link_url
                            link["status_code"] = None
                    
                    external_links.append(link)
                
                # Check if it's a media link
                if any(link_url.lower().endswith(ext) for ext in media_exts):
                    media_links.append(link)
                
                # Check if it's a document link
                if any(link_url.lower().endswith(ext) for ext in doc_exts):
                    document_links.append(link)
            
            result["categories"] = {
                "internal_links": {
                    "count": len(internal_links),
                    "links": internal_links
                },
                "external_links": {
                    "count": len(external_links),
                    "links": external_links
                },
                "media_links": {
                    "count": len(media_links),
                    "links": media_links
                },
                "document_links": {
                    "count": len(document_links),
                    "links": document_links
                }
            }
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to extract links: {str(e)}",
            "url": url
        }


# Define the schema for the extract_links command
EXTRACT_LINKS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "extract_links",
        "description": "Extract and optionally categorize all links from a webpage",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to extract links from"
                },
                "categorize": {
                    "type": "boolean",
                    "description": "Whether to categorize links by type (default: true)",
                    "default": True
                },
                "follow_redirects": {
                    "type": "boolean",
                    "description": "Whether to follow redirects when categorizing external links (default: false)",
                    "default": False
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("extract_links", extract_links, EXTRACT_LINKS_SCHEMA) 