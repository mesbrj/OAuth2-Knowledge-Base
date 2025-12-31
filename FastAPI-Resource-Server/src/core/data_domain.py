import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

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

    @model_validator(mode='before')
    @classmethod
    async def check_team_fields(cls, values) -> 'userEntity':
        if not values.get('team_id') and values.get('team_name'):
            from core.use_cases import dataManagerImpl

            db = dataManagerImpl()
            team_record = await db.process(
                operation = "read",
                entity = "teams",
                record_name = values.get('team_name')
            )
            if team_record:
                values['team_id'] = team_record.id
            else:
                raise ValueError(
                    f"Team '{values.get('team_name')}' does not exist."
                )
        return values


class teamEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: uuid.UUID | None = None
    name: str | None = None
    description: str | None = None
    manager_id: uuid.UUID | None = None
    entity: Literal["teams"] = "teams"