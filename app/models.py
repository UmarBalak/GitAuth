from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None

class Repository(BaseModel):
    name: str
    description: Optional[str] = None
    private: bool = False
