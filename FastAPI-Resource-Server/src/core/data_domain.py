import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr

# Entities

class userEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: uuid.UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    location: str | None = None
    team_name: str | None = None
    team_id: uuid.UUID | None = None
    entity: Literal["users"] = "users"


class teamEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: uuid.UUID | None = None
    name: str | None = None
    description: str | None = None
    manager_id: uuid.UUID | None = None
    entity: Literal["teams"] = "teams"