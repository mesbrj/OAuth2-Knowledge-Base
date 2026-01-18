from typing import List, Optional
from pydantic import BaseModel

class TokenData(BaseModel):
    """Domain model for validated token information."""
    sub: str  # Subject (user ID)
    username: str
    scopes: List[str]
    active: bool
    expires_at: Optional[int] = None


class UserInfo(BaseModel):
    """Domain model for user identity information."""
    id: str
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
