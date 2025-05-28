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