"""Web scrape command for SimpleAgent.

This module provides the web_scrape command for fetching and parsing webpage content.
"""

import json
import re
import random
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
from commands import register_command


class UserAgentManager:
    """Manages a rotating list of user agents for web requests."""
    
    def __init__(self):
        # Chrome versions - different from web_search
        self.chrome_versions = ['109.0.5414.119', '110.0.5481.177', '111.0.5563.64', 
                              '112.0.5615.49', '113.0.5672.63', '114.0.5735.106', 
                              '115.0.5790.102', '116.0.5845.96', '117.0.5938.62',
                              '118.0.5993.70', '119.0.6045.105', '120.0.6099.109',
                              '121.0.6167.85', '122.0.6261.39']
        
        # Firefox versions - different from web_search
        self.firefox_versions = ['103.0', '104.0', '105.0', '106.0', '107.0', '108.0',
                               '109.0', '110.0', '111.0', '112.0', '113.0', '114.0',
                               '115.0', '116.0', '117.0', '118.0', '119.0', '120.0',
                               '121.0', '122.0']
        
        # Safari versions - different from web_search
        self.safari_versions = ['16.0', '16.1', '16.2', '16.3', '16.4', '16.5',
                              '16.6', '17.0', '17.1', '17.2', '17.3', '17.4']
        
        # Operating systems - different combinations
        self.windows_versions = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Windows NT 10.0; WOW64',
            'Windows NT 11.0; WOW64',
            'Windows NT 10.0; ARM64',
            'Windows NT 11.0; ARM64'
        ]
        
        self.mac_versions = [
            'Macintosh; Intel Mac OS X 11_5_2',
            'Macintosh; Intel Mac OS X 12_0_1',
            'Macintosh; Intel Mac OS X 13_0_1',
            'Macintosh; Intel Mac OS X 14_0_1',
            'Macintosh; Apple M1 Mac OS X 11_5_2',
            'Macintosh; Apple M2 Mac OS X 13_0_1',
            'Macintosh; Apple M3 Mac OS X 14_0_1'
        ]
        
        self.linux_versions = [
            'X11; Ubuntu; Linux x86_64',
            'X11; Fedora; Linux x86_64',
            'X11; Debian; Linux x86_64',
            'X11; Linux i686',
            'X11; Linux armv7l',
            'X11; Linux aarch64'
        ]
        
        # Mobile devices - different set
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 16_0 like Mac OS X',
            'iPhone; CPU iPhone OS 17_0 like Mac OS X',
            'iPhone; CPU iPhone OS 17_1 like Mac OS X',
            'iPad; CPU OS 16_0 like Mac OS X',
            'iPad; CPU OS 17_0 like Mac OS X',
            'iPad; CPU OS 17_1 like Mac OS X',
            'Linux; Android 13; SM-G991B',
            'Linux; Android 14; SM-G991B',
            'Linux; Android 13; Pixel 6',
            'Linux; Android 14; Pixel 6',
            'Linux; Android 13; Pixel 7',
            'Linux; Android 14; Pixel 7',
            'Linux; Android 13; Pixel 8',
            'Linux; Android 14; Pixel 8',
            'Linux; Android 13; OnePlus 9 Pro',
            'Linux; Android 14; OnePlus 9 Pro',
            'Linux; Android 13; SM-S908B',
            'Linux; Android 14; SM-S908B',
            'Linux; Android 13; SM-S918B',
            'Linux; Android 14; SM-S918B'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        self.last_request_time = 0
        self.min_delay = 3  # Slightly longer delay for scraping
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome with variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                webkit_version = f"537.{random.randint(35, 45)}"
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
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(15, 25)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{version} Safari/{webkit_version}'
                )
        
        # Mobile browsers with variations
        for device in self.mobile_devices:
            # Mobile Chrome
            webkit_version = f"537.{random.randint(35, 45)}"
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/{webkit_version}'
            )
            
            # Mobile Safari (iOS)
            if 'iPhone' in device or 'iPad' in device:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(15, 25)}"
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
            'Sec-Fetch-Dest': random.choice(['document', 'empty', 'object']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site', 'cross-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store', 'private']),
            'Pragma': random.choice(['no-cache', '']),
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{random.randint(105, 125)}"',
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"']),
            'Sec-Ch-Ua-Platform-Version': f'"{random.randint(10, 14)}.0.0"'
        }
        
        return headers


# Create a singleton instance
user_agent_manager = UserAgentManager()


def web_scrape(url: str, extract_type: str = "all", max_content_length: int = 50000) -> Dict[str, Any]:
    """Fetch and parse content from a webpage.
    
    Args:
        url: The URL to scrape
        extract_type: What type of content to extract (all, article, main, content)
        max_content_length: Maximum length of content to return
        
    Returns:
        Dictionary containing the scraped content
    """
    try:
        # Get random headers for this request
        headers = user_agent_manager.get_headers()
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for element in soup(["script", "style", "noscript", "iframe", "footer", "nav", "aside"]):
            element.decompose()
            
        result = {
            "url": url,
            "title": soup.title.string if soup.title else None,
            "meta_description": None,
            "content": {}
        }
        
        # Get meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc:
            meta_desc = soup.find("meta", attrs={"property": "og:description"})
        if meta_desc:
            result["meta_description"] = meta_desc.get("content")
            
        # Try to get the main image if available
        main_image = soup.find("meta", attrs={"property": "og:image"})
        if main_image:
            result["main_image"] = main_image.get("content")
            
        # Content extraction strategy based on type
        content_found = False
        
        # 1. Look for structured content based on extract_type
        if extract_type in ["all", "article"] or not content_found:
            # Try to find article content - common in blog posts and news sites
            article_selectors = ["article", ".article", ".post", ".post-content", "#article", ".entry-content"]
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article and len(article.get_text(strip=True)) > 100:
                    result["content"]["article"] = article.get_text(separator="\n", strip=True)
                    content_found = True
                    break
                
        if extract_type in ["all", "main"] or not content_found:
            # Try to find main content - common in modern websites
            main_selectors = ["main", "#main", ".main", "#content", ".content", "#main-content", ".main-content"]
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content and len(main_content.get_text(strip=True)) > 100:
                    result["content"]["main"] = main_content.get_text(separator="\n", strip=True)
                    content_found = True
                    break
                    
        # 2. Extract semantic elements (for "content" type or fallback)
        if extract_type in ["all", "content"] or not content_found:
            # Look for div elements with content-related classes
            content_selectors = [".content", "#content", ".post-content", ".entry", ".entry-content", 
                               ".page-content", ".article-content", ".blog-content", ".main-content"]
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element and len(content_element.get_text(strip=True)) > 150:
                    result["content"]["content_div"] = content_element.get_text(separator="\n", strip=True)
                    content_found = True
                    break
            
        # 3. Collect all paragraphs as a fallback
        if not content_found or extract_type == "all":
            paragraphs = []
            for p in soup.find_all(["p", "div.p"]):
                text = p.get_text(strip=True)
                if text and len(text) > 50:  # Only include substantial paragraphs
                    paragraphs.append(text)
            
            # If we have paragraphs, join them
            if paragraphs:
                result["content"]["paragraphs"] = paragraphs
                content_found = True
                
        # 4. Extract headings for structure
        headings = []
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            text = h.get_text(strip=True)
            if text and len(text) > 2:  # Filter out empty headings
                headings.append({"level": h.name, "text": text})
        
        if headings:
            result["content"]["headings"] = headings
            
        # 5. Extract any lists that might contain valuable information
        lists = []
        for list_element in soup.find_all(["ul", "ol"]):
            # Check if it's not likely a navigation or menu list
            if "nav" not in list_element.get("class", []) and "menu" not in list_element.get("class", []):
                list_items = []
                for item in list_element.find_all("li"):
                    item_text = item.get_text(strip=True)
                    if item_text and len(item_text) > 10:
                        list_items.append(item_text)
                
                if list_items:  # Only add if there are meaningful items
                    lists.append({
                        "type": list_element.name,
                        "items": list_items
                    })
        
        if lists:
            result["content"]["lists"] = lists
            
        # 6. If after all this, we still have no content, try a more aggressive approach
        if not content_found:
            # Find the div with the most text content - likely to be main content
            divs = soup.find_all("div")
            max_text_length = 0
            max_text_div = None
            
            for div in divs:
                text_length = len(div.get_text(strip=True))
                if text_length > max_text_length and text_length > 200:
                    max_text_length = text_length
                    max_text_div = div
            
            if max_text_div:
                # This is our best guess at the main content
                result["content"]["extracted_content"] = max_text_div.get_text(separator="\n", strip=True)
                content_found = True
                
        # Truncate content if needed
        for key, value in result["content"].items():
            if isinstance(value, str) and len(value) > max_content_length:
                result["content"][key] = value[:max_content_length] + "... (content truncated)"
                result["truncated"] = True
                
        # Extract page language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            result["language"] = html_tag.get("lang")
            
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to scrape webpage: {str(e)}",
            "url": url
        }


# Define the schema for the web_scrape command
WEB_SCRAPE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_scrape",
        "description": "Fetch and parse content from a webpage",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                },
                "extract_type": {
                    "type": "string",
                    "description": "What type of content to extract (all, article, main, content)",
                    "enum": ["all", "article", "main", "content"],
                    "default": "all"
                },
                "max_content_length": {
                    "type": "integer",
                    "description": "Maximum length of content to return",
                    "default": 50000
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("web_scrape", web_scrape, WEB_SCRAPE_SCHEMA) 