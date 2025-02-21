from fastapi import HTTPException
import httpx
from typing import List
from ..models import Repository
from ..config import settings

class GitHubAPI:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    async def _make_request(self, method: str, url: str, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"https://api.github.com{url}",
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("message", "GitHub API error")
                )
            
            return response.json()
    
    async def list_repositories(self) -> List[Repository]:
        """List user's repositories"""
        data = await self._make_request("GET", "/user/repos")
        return [
            Repository(
                name=repo["name"],
                description=repo.get("description"),
                private=repo["private"]
            )
            for repo in data
        ]
    