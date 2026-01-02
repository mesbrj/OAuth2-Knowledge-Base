from uuid import UUID
from typing import Literal
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
    entity: Literal["users"] = "users"


class teamEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    manager_name: str | None = None
    manager_id: UUID | None = None
    entity: Literal["teams"] = "teams"