from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/callback"
    APP_HOST: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()