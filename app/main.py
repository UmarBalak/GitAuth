from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
import datetime
from dotenv import load_dotenv
import os
from typing import List
from config import settings
from auth import github
from auth.github_repos import GitHubAPI
from models import Repository, User

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
async def github_login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=user:email"
    return RedirectResponse(url=github_auth_url)

@app.get("/callback")
async def github_callback(code: str):
    try:
        access_token = await github.get_access_token(code)
        user = await github.get_user_data(access_token)
        jwt_token = create_jwt_token(user, access_token)

        return JSONResponse(content={
            "token": jwt_token,
            "username": user.username,
            "avatar_url": user.avatar_url or ''
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

async def get_github_api(authorization: str = Header(None)) -> GitHubAPI:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token = authorization.split("Bearer ")[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return GitHubAPI(payload["access_token"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/repos", response_model=List[Repository])
async def list_repositories(github: GitHubAPI = Depends(get_github_api)):
    return await github.list_repositories()

