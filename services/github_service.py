import httpx
import os
import re
from typing import Optional, List, Dict, Any
from models.issue import GitHubIssue, GitHubUser, GitHubLabel, GitHubComment

try:
    import upsonic
    UPSONIC_AVAILABLE = True
except ImportError:
    UPSONIC_AVAILABLE = False

# Custom GitHub Tool for Upsonic
class GitHubTool:
    """Custom tool for GitHub API operations"""

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def fetch_github_issue(self, github_url: str) -> Dict[str, Any]:
        """Fetch GitHub issue data and return structured information"""
        try:
            owner, repo, issue_number = self.parse_github_url(github_url)

            async with httpx.AsyncClient() as client:
                # Fetch issue details
                issue_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}",
                    headers=self.headers
                )
                issue_response.raise_for_status()
                issue_data = issue_response.json()

                # Fetch comments
                comments_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments",
                    headers=self.headers
                )
                comments_response.raise_for_status()
                comments_data = comments_response.json()

                return {
                    "issue": issue_data,
                    "comments": comments_data
                }

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
            raise
        except Exception as e:
            print(f"Error fetching GitHub issue: {str(e)}")
            raise

# Apply Upsonic decorator if available
if UPSONIC_AVAILABLE:
    GitHubTool = upsonic.tool()(GitHubTool)
    # Also decorate the method
    GitHubTool.fetch_github_issue = upsonic.tool()(GitHubTool.fetch_github_issue)


    async def fetch_issue(self, github_url: str) -> GitHubIssue:
        """Legacy method for backward compatibility"""
        try:
            result = await self.fetch_github_issue(github_url)

            # Convert to legacy GitHubIssue model
            issue_data = result["issue"]
            comments_data = result["comments"]

            user = GitHubUser(
                login=issue_data["user"]["login"],
                id=issue_data["user"]["id"],
                avatar_url=issue_data["user"]["avatar_url"],
                html_url=issue_data["user"]["html_url"]
            )

            labels = [
                GitHubLabel(
                    name=label["name"],
                    color=label["color"],
                    description=label.get("description")
                ) for label in issue_data.get("labels", [])
            ]

            comments = [
                GitHubComment(
                    id=comment["id"],
                    user=GitHubUser(
                        login=comment["user"]["login"],
                        id=comment["user"]["id"],
                        avatar_url=comment["user"]["avatar_url"],
                        html_url=comment["user"]["html_url"]
                    ),
                    body=comment["body"],
                    created_at=comment["created_at"],
                    updated_at=comment["updated_at"]
                ) for comment in comments_data
            ]

            issue = GitHubIssue(
                id=issue_data["id"],
                number=issue_data["number"],
                title=issue_data["title"],
                body=issue_data.get("body"),
                user=user,
                labels=labels,
                state=issue_data["state"],
                created_at=issue_data["created_at"],
                updated_at=issue_data["updated_at"],
                html_url=issue_data["html_url"],
                comments=comments
            )

            return issue

        except Exception as e:
            print(f"Error in legacy fetch_issue: {str(e)}")
            raise

# Legacy GitHubService class for backward compatibility
class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def parse_github_url(self, url: str) -> tuple[str, str, int]:
        """Parse GitHub URL to extract owner, repo, and issue number"""
        pattern = r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.match(pattern, url)
        if not match:
            raise ValueError("Invalid GitHub issue URL format")
        
        owner, repo, issue_number = match.groups()
        return owner, repo, int(issue_number)
    
    async def fetch_issue(self, github_url: str) -> GitHubIssue:
        """Fetch issue data from GitHub API"""
        try:
            owner, repo, issue_number = self.parse_github_url(github_url)
            
            async with httpx.AsyncClient() as client:
                # Fetch issue details
                issue_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}",
                    headers=self.headers
                )
                issue_response.raise_for_status()
                issue_data = issue_response.json()
                
                # Fetch comments
                comments_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments",
                    headers=self.headers
                )
                comments_response.raise_for_status()
                comments_data = comments_response.json()
                
                # Convert to our models
                user = GitHubUser(
                    login=issue_data["user"]["login"],
                    id=issue_data["user"]["id"],
                    avatar_url=issue_data["user"]["avatar_url"],
                    html_url=issue_data["user"]["html_url"]
                )
                
                labels = [
                    GitHubLabel(
                        name=label["name"],
                        color=label["color"],
                        description=label.get("description")
                    ) for label in issue_data.get("labels", [])
                ]
                
                comments = [
                    GitHubComment(
                        id=comment["id"],
                        user=GitHubUser(
                            login=comment["user"]["login"],
                            id=comment["user"]["id"],
                            avatar_url=comment["user"]["avatar_url"],
                            html_url=comment["user"]["html_url"]
                        ),
                        body=comment["body"],
                        created_at=comment["created_at"],
                        updated_at=comment["updated_at"]
                    ) for comment in comments_data
                ]
                
                issue = GitHubIssue(
                    id=issue_data["id"],
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data.get("body"),
                    user=user,
                    labels=labels,
                    state=issue_data["state"],
                    created_at=issue_data["created_at"],
                    updated_at=issue_data["updated_at"],
                    html_url=issue_data["html_url"],
                    comments=comments
                )
                
                return issue
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
            raise
        except Exception as e:
            print(f"Error fetching GitHub issue: {str(e)}")
            raise
