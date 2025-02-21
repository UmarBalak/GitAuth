from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "https://gitauth-iza6.onrender.com/login"
    APP_HOST: str = "https://ai-2namqliw7-ubaid-khans-projects-c47937ab.vercel.app"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()