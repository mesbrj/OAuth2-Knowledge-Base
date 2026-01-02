from uuid import UUID
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# Entities

class userEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    location: str | None = None
    team_name: str | None = None
    team_id: UUID | None = None
    team: Optional['teamEntity'] = None
    manages: Optional['teamEntity'] = None
    projects: Optional[list['projectEntity']] = None
    entity: Literal["users"] = "users"


class teamEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    manager_name: str | None = None
    manager_id: UUID | None = None
    manager: Optional['userEntity'] = None
    users: Optional[list[userEntity]] = None
    entity: Literal["teams"] = "teams"


class projectEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    users: Optional[list[userEntity]] = None


class projectRoleEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    projects: Optional[list[projectEntity]] = None
    entity: Literal["project_roles"] = "project_roles"


class startedProjectEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    project_name: str | None = None
    project_id: UUID | None = None
    user_name: str | None = None
    user_id: UUID | None = None
    role_name: str | None = None
    role_id: UUID | None = None
    role: projectRoleEntity | None = None
    entity: Literal["started_projects"] = "started_projects"