"""
GitHub repository search command for SimpleAgent.

This module provides the github_repo_search command for searching GitHub repositories
with specific criteria and retrieving their information.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from commands import register_command


class GitHubSearchManager:
    """Manages GitHub API search requests with rate limiting protection."""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_delay = 2  # Minimum delay between requests in seconds
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'SimpleAgent-GitHub-Search'
        }
        
    def _add_auth_header(self, token: Optional[str] = None):
        """Add authentication header if token is provided."""
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def search_repositories(
        self,
        query: str,
        min_stars: Optional[int] = None,
        min_forks: Optional[int] = None,
        language: Optional[str] = None,
        created_after: Optional[str] = None,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search GitHub repositories with various criteria.
        
        Args:
            query: The search query
            min_stars: Minimum number of stars
            min_forks: Minimum number of forks
            language: Programming language filter
            created_after: Filter repositories created after this date (YYYY-MM-DD)
            sort: Sort results by (stars, forks, updated)
            order: Sort order (asc, desc)
            per_page: Number of results per page
            token: GitHub API token for authentication
            
        Returns:
            Dictionary containing search results
        """
        import time
        
        # Add delay between requests
        current_time = time.time()
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()
        
        # Build the search query
        search_query = query
        
        if min_stars:
            search_query += f" stars:>={min_stars}"
        if min_forks:
            search_query += f" forks:>={min_forks}"
        if language:
            search_query += f" language:{language}"
        if created_after:
            search_query += f" created:>={created_after}"
            
        # Add authentication if token provided
        self._add_auth_header(token)
        
        # Make the API request
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': search_query,
            'sort': sort,
            'order': order,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }


def github_repo_search(
    query: str,
    min_stars: Optional[int] = None,
    min_forks: Optional[int] = None,
    language: Optional[str] = None,
    created_after: Optional[str] = None,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 10,
    token: Optional[str] = None,
    save_readme: bool = False,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search GitHub repositories with various criteria and optionally save README contents.
    
    Args:
        query: The search query
        min_stars: Minimum number of stars
        min_forks: Minimum number of forks
        language: Programming language filter
        created_after: Filter repositories created after this date (YYYY-MM-DD)
        sort: Sort results by (stars, forks, updated)
        order: Sort order (asc, desc)
        per_page: Number of results per page
        token: GitHub API token for authentication
        save_readme: Whether to save README contents to a file
        output_file: File path to save README contents (default: project_info.md)
        
    Returns:
        Dictionary containing search results and repository information
    """
    # Initialize search manager
    search_manager = GitHubSearchManager()
    
    # Perform the search
    search_results = search_manager.search_repositories(
        query=query,
        min_stars=min_stars,
        min_forks=min_forks,
        language=language,
        created_after=created_after,
        sort=sort,
        order=order,
        per_page=per_page,
        token=token
    )
    
    if "error" in search_results:
        return search_results
    
    # Process results
    processed_results = []
    for repo in search_results.get("items", []):
        repo_info = {
            "name": repo["full_name"],
            "description": repo["description"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "language": repo["language"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "topics": repo["topics"],
            "license": repo["license"]["name"] if repo["license"] else None,
            "open_issues": repo["open_issues_count"],
            "default_branch": repo["default_branch"]
        }
        
        # Get README content if requested
        if save_readme:
            try:
                readme_url = f"{search_manager.base_url}/repos/{repo['full_name']}/readme"
                readme_response = requests.get(readme_url, headers=search_manager.headers)
                readme_response.raise_for_status()
                readme_content = readme_response.content.decode('utf-8')
                repo_info["readme_content"] = readme_content
                
                # Save README to file if output_file specified
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {repo['full_name']}\n\n")
                        f.write(f"URL: {repo['html_url']}\n\n")
                        f.write(f"Stars: {repo['stargazers_count']}\n")
                        f.write(f"Forks: {repo['forks_count']}\n")
                        f.write(f"Language: {repo['language']}\n\n")
                        f.write("## Description\n\n")
                        f.write(f"{repo['description']}\n\n")
                        f.write("## README\n\n")
                        f.write(readme_content)
            except Exception as e:
                repo_info["readme_error"] = str(e)
        
        processed_results.append(repo_info)
    
    return {
        "total_count": search_results["total_count"],
        "repositories": processed_results
    }


# Register the command
GITHUB_REPO_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "github_repo_search",
        "description": "Search GitHub repositories with various criteria and optionally save README contents",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "min_stars": {
                    "type": "integer",
                    "description": "Minimum number of stars"
                },
                "min_forks": {
                    "type": "integer",
                    "description": "Minimum number of forks"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language filter"
                },
                "created_after": {
                    "type": "string",
                    "description": "Filter repositories created after this date (YYYY-MM-DD)"
                },
                "sort": {
                    "type": "string",
                    "description": "Sort results by (stars, forks, updated)",
                    "enum": ["stars", "forks", "updated"]
                },
                "order": {
                    "type": "string",
                    "description": "Sort order",
                    "enum": ["asc", "desc"]
                },
                "per_page": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "minimum": 1,
                    "maximum": 100
                },
                "token": {
                    "type": "string",
                    "description": "GitHub API token for authentication"
                },
                "save_readme": {
                    "type": "boolean",
                    "description": "Whether to save README contents to a file"
                },
                "output_file": {
                    "type": "string",
                    "description": "File path to save README contents"
                }
            },
            "required": ["query"]
        }
    }
}

register_command("github_repo_search", github_repo_search, GITHUB_REPO_SEARCH_SCHEMA) 