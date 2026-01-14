from typing import Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr

class createUser(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    team_name: str | None = None
    team_id: UUID | None = None
    entity: Literal["users"] = "users"


class createTeam(BaseModel):
    name: str
    description: str | None = None
    manager_email: EmailStr | None = None
    manager_id: UUID | None = None
    entity: Literal["teams"] = "teams"


class createResponse(BaseModel):
    record_id: UUID
    record_name: str | None = None


class readEntity(BaseModel):
    record_id: UUID | None = None
    record_name: str | None = None
    entity: Literal["users", "teams"]


class queryPagination(BaseModel):
    offset: int | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] = "asc"


class readUserResponse(createUser):
    id: UUID


class readTeamResponse(createTeam):
    id: UUID
    manager: readUserResponse | None = None
    users: list[readUserResponse] | None = None