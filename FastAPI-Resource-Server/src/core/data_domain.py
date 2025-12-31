from pydantic import BaseModel, ConfigDict, EmailStr, model_validator
import uuid

# Entities

class userEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: uuid.UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    location: str | None = None
    team_id: uuid.UUID | None = None
    team: str | None = None

    @model_validator(mode='before')
    @classmethod
    def check_mutually_exclusive_fields(cls, values) -> 'userEntity':
        if not isinstance(values, dict):
            raise ValueError("Input must be a dictionary.")
        if values.get('team_id') is not None and values.get('team') is not None:
            raise ValueError("Only one of 'team_id' or 'team' should be provided.")
        if values.get('id') is not None and values.get('name') is not None:
            raise ValueError("Only one of 'id' or 'name' should be provided.")
        return values
