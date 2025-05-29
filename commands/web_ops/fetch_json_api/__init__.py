"""
Fetch JSON API command for SimpleAgent.

This module provides the fetch_json_api command for retrieving JSON data from APIs.
"""

import json
import random
import requests
from typing import Dict, Any, Optional, Union, List
from commands import register_command


class UserAgentManager:
    """Manages a rotating list of user agents for web requests."""
    
    def __init__(self):
        # Chrome versions - different from others
        self.chrome_versions = ['120.0.6099.109', '121.0.6167.85', '122.0.6261.39', 
                              '123.0.6312.58', '124.0.6367.79', '125.0.6422.60',
                              '126.0.6478.40', '127.0.6533.40', '128.0.6587.40']
        
        # Firefox versions - different from others
        self.firefox_versions = ['120.0', '121.0', '122.0', '123.0', '124.0', '125.0',
                               '126.0', '127.0', '128.0', '129.0', '130.0']
        
        # Safari versions - different from others
        self.safari_versions = ['17.0', '17.1', '17.2', '17.3', '17.4', '17.5',
                              '17.6', '17.7', '18.0', '18.1', '18.2']
        
        # Operating systems - different combinations
        self.windows_versions = [
            'Windows NT 11.0; Win64; x64',
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; ARM64',
            'Windows NT 10.0; ARM64',
            'Windows NT 11.0; x64',
            'Windows NT 10.0; x64'
        ]
        
        self.mac_versions = [
            'Macintosh; Apple M3 Mac OS X 14_0_1',
            'Macintosh; Apple M2 Mac OS X 14_0_1',
            'Macintosh; Apple M1 Mac OS X 14_0_1',
            'Macintosh; Apple M3 Pro Mac OS X 14_0_1',
            'Macintosh; Apple M2 Pro Mac OS X 14_0_1',
            'Macintosh; Apple M1 Pro Mac OS X 14_0_1'
        ]
        
        self.linux_versions = [
            'X11; Linux aarch64',
            'X11; Linux x86_64',
            'X11; Ubuntu; Linux x86_64',
            'X11; Fedora; Linux x86_64',
            'X11; Debian; Linux x86_64'
        ]
        
        # Mobile devices - different set
        self.mobile_devices = [
            'iPhone; CPU iPhone OS 17_3 like Mac OS X',
            'iPhone; CPU iPhone OS 17_4 like Mac OS X',
            'iPhone; CPU iPhone OS 18_0 like Mac OS X',
            'iPad; CPU OS 17_3 like Mac OS X',
            'iPad; CPU OS 17_4 like Mac OS X',
            'iPad; CPU OS 18_0 like Mac OS X',
            'Linux; Android 14; Pixel 8',
            'Linux; Android 14; Pixel 8 Pro',
            'Linux; Android 14; SM-S928B',
            'Linux; Android 14; SM-S918B',
            'Linux; Android 14; OnePlus 12'
        ]
        
        # Build the full user agent list
        self.user_agents = self._generate_user_agents()
        self.last_request_time = 0
        self.min_delay = 1.5  # Shorter delay for API calls
        
    def _generate_user_agents(self) -> List[str]:
        """Generate a diverse list of user agents."""
        agents = []
        
        # Desktop Chrome with variations
        for os in self.windows_versions + self.mac_versions + self.linux_versions:
            for version in self.chrome_versions:
                webkit_version = f"537.{random.randint(55, 65)}"
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
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(35, 45)}"
                agents.append(
                    f'Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                    f'Version/{version} Safari/{webkit_version}'
                )
        
        # Mobile browsers with variations
        for device in self.mobile_devices:
            # Mobile Chrome
            webkit_version = f"537.{random.randint(55, 65)}"
            agents.append(
                f'Mozilla/5.0 ({device}) AppleWebKit/{webkit_version} (KHTML, like Gecko) '
                f'Chrome/{random.choice(self.chrome_versions)} Mobile Safari/{webkit_version}'
            )
            
            # Mobile Safari (iOS)
            if 'iPhone' in device or 'iPad' in device:
                webkit_version = f"605.{random.randint(1, 2)}.{random.randint(35, 45)}"
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
            'Accept': 'application/json,text/plain,*/*',
            'Accept-Language': random.choice(accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(random.randint(0, 1)),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(['empty', 'object', 'script']),
            'Sec-Fetch-Mode': random.choice(['cors', 'no-cors', 'websocket']),
            'Sec-Fetch-Site': random.choice(['same-origin', 'same-site', 'cross-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['no-cache', 'no-store', 'private', 'must-revalidate']),
            'Pragma': random.choice(['no-cache', '']),
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{random.randint(120, 140)}"',
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"']),
            'Sec-Ch-Ua-Platform-Version': f'"{random.randint(10, 14)}.0.0"',
            'Sec-Ch-Ua-Full-Version': f'"{random.randint(120, 140)}.0.0.0"',
            'Origin': 'https://example.com',
            'Referer': 'https://example.com/'
        }
        
        return headers


# Create a singleton instance
user_agent_manager = UserAgentManager()


def fetch_json_api(
    url: str, 
    method: str = "GET", 
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    auth_type: Optional[str] = None,
    auth_token: Optional[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Fetch JSON data from an API endpoint.
    
    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        params: Query parameters for the request
        headers: Custom headers for the request
        data: Data to send in the request body (for POST, PUT, etc.)
        auth_type: Authentication type (basic, bearer, api_key)
        auth_token: Authentication token or API key
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing the API response
    """
    try:
        # Set up default headers with user agent
        request_headers = user_agent_manager.get_headers()
        request_headers["Accept"] = "application/json"
        
        # Add custom headers if provided
        if headers:
            request_headers.update(headers)
            
        # Handle authentication
        if auth_type and auth_token:
            if auth_type.lower() == "bearer":
                request_headers["Authorization"] = f"Bearer {auth_token}"
            elif auth_type.lower() == "basic":
                request_headers["Authorization"] = f"Basic {auth_token}"
            elif auth_type.lower() == "api_key":
                # Default to using auth_token as an API key in header
                # If the API requires it as a param, use the params argument instead
                request_headers["X-API-Key"] = auth_token
                
        # Prepare request arguments
        request_args = {
            "url": url,
            "headers": request_headers,
            "timeout": timeout
        }
        
        # Add query parameters if provided
        if params:
            request_args["params"] = params
            
        # Add request body if provided for appropriate methods
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            # Check if data should be JSON or form data
            if isinstance(data, dict):
                if request_headers.get("Content-Type") == "application/x-www-form-urlencoded":
                    request_args["data"] = data
                else:
                    request_args["json"] = data
            else:
                request_args["data"] = data
        
        # Make the request
        response = requests.request(method.upper(), **request_args)
        
        # Attempt to parse JSON response
        try:
            json_response = response.json()
        except json.JSONDecodeError:
            # Return text response if not JSON
            return {
                "success": response.ok,
                "status_code": response.status_code,
                "url": url,
                "method": method.upper(),
                "is_json": False,
                "text_content": response.text[:10000] if len(response.text) > 10000 else response.text,
                "headers": dict(response.headers)
            }
        
        # Return successful JSON response
        result = {
            "success": response.ok,
            "status_code": response.status_code,
            "url": url,
            "method": method.upper(),
            "is_json": True,
            "data": json_response,
            "headers": dict(response.headers)
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out",
            "success": False,
            "url": url,
            "method": method.upper()
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection error - could not connect to the API",
            "success": False,
            "url": url,
            "method": method.upper()
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch API data: {str(e)}",
            "success": False,
            "url": url,
            "method": method.upper()
        }


# Define the schema for the fetch_json_api command
FETCH_JSON_API_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_json_api",
        "description": "Fetch JSON data from an API endpoint with various options",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method (GET, POST, PUT, DELETE, etc.)",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
                    "default": "GET"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters for the request",
                    "additionalProperties": {"type": "string"}
                },
                "headers": {
                    "type": "object",
                    "description": "Custom headers for the request",
                    "additionalProperties": {"type": "string"}
                },
                "data": {
                    "type": "object",
                    "description": "Data to send in the request body (for POST, PUT, etc.)",
                    "additionalProperties": {"type": "string"}
                },
                "auth_type": {
                    "type": "string",
                    "description": "Authentication type (basic, bearer, api_key)",
                    "enum": ["basic", "bearer", "api_key"]
                },
                "auth_token": {
                    "type": "string",
                    "description": "Authentication token or API key"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("fetch_json_api", fetch_json_api, FETCH_JSON_API_SCHEMA) 