from fastapi import APIRouter, Depends, status
from adapter.rest.func_deps import (
    entity_create,
    entity_read_by_id,
    entity_read_paginated
)
from adapter.rest.dto import (
    createResponse, createUser, createTeam,
    readUserResponse, readTeamResponse
)

health_routes = APIRouter()
crud_routes = APIRouter()

@health_routes.get("/health", tags = ["Health"])
def health_check():
    return {"status": "ok"}


@crud_routes.post(
    "/users",
    response_model = createResponse,
    status_code = status.HTTP_201_CREATED,
    tags = ["Users"]
    )
async def create_user(
    body: createUser,
    response: createResponse = Depends(entity_create)
    ):
    return response


@crud_routes.post(
    "/teams",
    response_model = createResponse,
    status_code = status.HTTP_201_CREATED,
    tags = ["Teams"]
    )
async def create_team(
    body: createTeam,
    response: createResponse = Depends(entity_create)
    ):
    return response


@crud_routes.get(
    "/users/{record_id}",
    response_model = readUserResponse,
    status_code = status.HTTP_200_OK,
    tags = ["Users"]
    )
async def read_user_by_id(
    record_id: str,
    response: readUserResponse = Depends(entity_read_by_id("users"))
    ):
    return response


@crud_routes.get(
    "/users",
    response_model = list[readUserResponse],
    status_code = status.HTTP_200_OK,
    tags = ["Users"]
    )
async def read_all_users(response: list[readUserResponse] = Depends(entity_read_paginated("users"))):
    return response


@crud_routes.get(
    "/teams/{record_id}",
    response_model = readTeamResponse,
    status_code = status.HTTP_200_OK,
    tags = ["Teams"]
    )
async def read_team_by_id(
    record_id: str,
    response: readTeamResponse = Depends(entity_read_by_id("teams"))
    ):
    return response


@crud_routes.get(
    "/teams",
    response_model = list[readTeamResponse],
    status_code = status.HTTP_200_OK,
    tags = ["Teams"]
    )
async def read_all_teams(response: list[readTeamResponse] = Depends(entity_read_paginated("teams"))):
    return response
