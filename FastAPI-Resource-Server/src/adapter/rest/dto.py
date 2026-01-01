import uuid
from typing import Literal
from pydantic import BaseModel, EmailStr

# Response models

# Request models

class createUser(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    team_name: str | None = None
    entity: Literal["users"] = "users"

class createTeam(BaseModel):
    name: str
    description: str | None = None
    manager_name: str | None = None
    entity: Literal["teams"] = "teams"

# Query models

# Header models