from fastapi import APIRouter, Depends, status, Query
from adapter.rest.func_deps import entity_create, entity_read
from adapter.rest.dto import (
    createResponse, createUser, createTeam,
    readEntity, queryPagination, readUserResponse, readTeamResponse
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
    "/users/{user_id}",
    response_model = readUserResponse,
    status_code = status.HTTP_200_OK,
    tags = ["Users"]
    )
async def read_user_by_id(user_id: str):
    return await entity_read(
        query = readEntity(record_id = user_id, entity = "users")
    )


@crud_routes.get(
    "/users",
    response_model = list[readUserResponse],
    status_code = status.HTTP_200_OK,
    tags = ["Users"]
    )
async def read_all_users(
    offset: int | None = Query(None, ge = 0),
    limit: int | None = Query(None, ge = 1, le = 100),
    order: str = Query("asc", pattern = "^(asc|desc)$")
    ):
    return await entity_read(
        query = readEntity(entity = "users"),
        pagination = queryPagination(offset = offset, limit = limit, order = order)
    )


@crud_routes.get(
    "/teams/{team_id}",
    response_model = readTeamResponse,
    status_code = status.HTTP_200_OK,
    tags = ["Teams"]
    )
async def read_team_by_id(team_id: str):
    return await entity_read(
        query = readEntity(record_id = team_id, entity = "teams")
    )


@crud_routes.get(
    "/teams",
    response_model = list[readTeamResponse],
    status_code = status.HTTP_200_OK,
    tags = ["Teams"]
    )
async def read_all_teams(
    offset: int | None = Query(None, ge = 0),
    limit: int | None = Query(None, ge = 1, le = 100),
    order: str = Query("asc", pattern = "^(asc|desc)$")
    ):
    return await entity_read(
        query = readEntity(entity = "teams"),
        pagination = queryPagination(offset = offset, limit = limit, order = order)
    )
