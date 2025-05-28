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