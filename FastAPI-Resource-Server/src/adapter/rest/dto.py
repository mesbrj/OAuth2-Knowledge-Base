from typing import Literal
from uuid import UUID
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


class createResponse(BaseModel):
    record_id: UUID
    record_name: str
    entity: Literal["users", "teams"]


class readEntity(BaseModel):
    record_id: UUID
    entity: Literal["users", "teams"]


class queryEntity(BaseModel):
    offset: int | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None
    entity: Literal["users", "teams"]


class readUserResponse(createUser):
    id: UUID
    team_id: UUID | None = None


class readTeamResponse(createTeam):
    id: UUID
    manager_id: UUID | None = None
    manager: readUserResponse | None = None
    users: list[readUserResponse] | None = None