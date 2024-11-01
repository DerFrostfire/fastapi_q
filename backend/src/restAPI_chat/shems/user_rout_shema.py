from typing import Optional

from pydantic import BaseModel, Field
from src.auth.auth_shema import AuthMe

class UserGet(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    created_at: str
    updated_at: str
    nick: Optional[str]

class UserStatus(BaseModel):
    id: int
    status: str = Field(..., pattern="^(offline|online)$")
    online_at: str