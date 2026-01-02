from typing import Literal
from pydantic import BaseModel, EmailStr

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

class readEntity(BaseModel):
    record_name: str
    entity: Literal["users", "teams"]