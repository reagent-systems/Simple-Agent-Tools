"""
Paste to pastebin command for SimpleAgent.

This module provides the paste_to_pastebin command for posting content to dpaste.org (anonymous, no API key required).
"""

import requests
from typing import Dict, Any, Optional
from commands import register_command


class PastebinManager:
    """Manages posting to dpaste.org pastebin service."""
    
    def __init__(self):
        """Initialize the Pastebin Manager."""
        self.dpaste_url = "https://dpaste.org/api/"
    
    def post_to_dpaste(self, content: str, title: str = "", language: str = "text", expire: str = "1week") -> Dict[str, Any]:
        """
        Post content to dpaste.org (free, no API key required).
        
        Args:
            content: The content to post
            title: Optional title for the paste
            language: Syntax highlighting language
            expire: Expiration time (1hour, 1day, 1week, 1month, never)
            
        Returns:
            Dictionary containing the result
        """
        try:
            data = {
                "content": content,
                "title": title or "Untitled Paste",
                "syntax": language,
                "expiry_days": self._convert_expire_to_days(expire)
            }
            
            response = requests.post(
                self.dpaste_url,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                # dpaste returns the URL directly in the response text
                paste_url = response.text.strip()
                return {
                    "success": True,
                    "url": paste_url,
                    "service": "dpaste.org",
                    "title": title or "Untitled Paste",
                    "expiry": expire
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "service": "dpaste.org"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "service": "dpaste.org"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "service": "dpaste.org"
            }
    
    def _convert_expire_to_days(self, expire: str) -> int:
        """Convert expire string to days for dpaste."""
        expire_map = {
            "1hour": 0,
            "1day": 1,
            "1week": 7,
            "1month": 30,
            "never": 0
        }
        return expire_map.get(expire.lower(), 7)


def paste_to_pastebin(
    content: str,
    title: Optional[str] = None,
    language: str = "text",
    expire: str = "1week"
) -> Dict[str, Any]:
    """
    Paste content to dpaste.org pastebin service.
    
    Args:
        content: The content to paste
        title: Optional title for the paste
        language: Programming language for syntax highlighting (text, python, javascript, json, html, css, etc.)
        expire: Expiration time (1hour, 1day, 1week, 1month, never)
        
    Returns:
        Dictionary containing the paste URL and metadata
    """
    try:
        if not content or not content.strip():
            return {
                "success": False,
                "error": "Content cannot be empty",
                "service": "dpaste.org"
            }
        
        # Initialize pastebin manager
        manager = PastebinManager()
        
        # Post to dpaste
        return manager.post_to_dpaste(
            content=content,
            title=title or "",
            language=language,
            expire=expire
        )
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "service": "dpaste.org"
        }


# Define the schema for the paste_to_pastebin command
PASTE_TO_PASTEBIN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paste_to_pastebin",
        "description": "Paste content to dpaste.org and get a shareable URL (anonymous, no API key required)",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to paste to pastebin"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the paste (default: 'Untitled Paste')"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language for syntax highlighting",
                    "enum": ["text", "python", "javascript", "js", "json", "html", "css", "xml", "sql", "bash", "shell", "java", "c", "cpp", "csharp", "php", "ruby", "go", "rust"],
                    "default": "text"
                },
                "expire": {
                    "type": "string", 
                    "description": "When the paste should expire",
                    "enum": ["1hour", "1day", "1week", "1month", "never"],
                    "default": "1week"
                }
            },
            "required": ["content"]
        }
    }
}

# Register the command
register_command("paste_to_pastebin", paste_to_pastebin, PASTE_TO_PASTEBIN_SCHEMA) 