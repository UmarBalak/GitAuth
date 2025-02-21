from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
import datetime
from dotenv import load_dotenv
import os
from typing import List
from .config import settings
from .auth import github
from .auth.github_repos import GitHubAPI
from .models import User

# Load environment variables
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate JWT Token
def create_jwt_token(user: User, access_token: str):
    payload = {
        "sub": user.username,
        "access_token": access_token,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@app.get("/")
async def landing_page():
    return JSONResponse(content={"message": "Welcome to the AI Collaboration Platform"})

@app.get("/login")
async def github_login(request: Request):
    code = request.query_params.get("code")
    if not code:
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=user:email"
        return RedirectResponse(url=github_auth_url)
    
    try:
        access_token = await github.get_access_token(code)
        user = await github.get_user_data(access_token)
        jwt_token = create_jwt_token(user, access_token)
        
        github_api = GitHubAPI(access_token)
        repositories = await github_api.list_repositories()
        repositories_data = [repo.dict() for repo in repositories]

        return JSONResponse(content={
            "token": jwt_token,
            "username": user.username,
            "avatar_url": user.avatar_url or '',
            "repositories": repositories_data
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")