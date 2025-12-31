import uuid
from typing import Literal
from pydantic import BaseModel, EmailStr

# Response models

# Request models

class createUser(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    team_id: uuid.UUID | None = None
    team: str | None = None
    entity: Literal["users"] = "users"

# Query models

# Header models