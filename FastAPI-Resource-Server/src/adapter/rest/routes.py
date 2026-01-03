from fastapi import APIRouter, Depends, status
from adapter.rest.func_deps import entityCreate
from adapter.rest.dto import createResponse, createUser, createTeam

health_routes = APIRouter()

crud_routes = APIRouter()

@health_routes.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@crud_routes.post(
    "/users",
    response_model=createResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"]
)
async def create_user(
    body: createUser,
    response: createResponse = Depends(entityCreate)
):
    return response


@crud_routes.post(
    "/teams",
    response_model=createResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Teams"]
)
async def create_team(
    body: createTeam,
    response: createResponse = Depends(entityCreate)
):
    return response

