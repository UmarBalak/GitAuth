from fastapi import HTTPException
import httpx
from ..models import User
from ..config import settings

async def get_access_token(code: str) -> str:
    """Exchange code for access token"""
    token_url = "https://github.com/login/oauth/access_token"
    token_params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            params=token_params,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        return response.json().get("access_token")

async def get_user_data(access_token: str) -> User:
    """Fetch user data from GitHub API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user data")
        
        user_data = response.json()
        return User(
            username=user_data["login"],
            email=user_data.get("email"),
            avatar_url=user_data.get("avatar_url")
        )