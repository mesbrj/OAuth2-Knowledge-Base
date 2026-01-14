
from fastapi import Query
from ports.inbound import inbound_factory
from adapter.rest.dto import (
    createUser, createTeam, createResponse,
    readEntity, queryPagination, readUserResponse, readTeamResponse
)


async def entity_create(body: createUser | createTeam) -> createResponse:
    data_manager = inbound_factory("data")
    new_rec = await data_manager.process(
        operation = "create",
        entity = body.entity,
        **body.model_dump(exclude = {"entity"})
    )
    return createResponse(
        record_id = new_rec.id,
        record_name = new_rec.name,
    )


async def entity_read(
    query: readEntity,
    pagination: queryPagination | None = None
) -> readUserResponse | readTeamResponse | list[readUserResponse] | list[readTeamResponse]:
    data_manager = inbound_factory("data")
    if query.record_id:
        record = await data_manager.process(
            operation = "read",
            entity = query.entity,
            record_id = query.record_id
        )
        return record
    records = await data_manager.process(
        operation = "read",
        entity = query.entity,
        offset = pagination.offset if pagination else None,
        limit = pagination.limit if pagination else None,
        order = pagination.order if pagination else "asc"
    )
    return records


def entity_read_by_id(entity_type: str):
    async def dependency(record_id: str):
        return await entity_read(query = readEntity(record_id = record_id, entity = entity_type))
    return dependency


def entity_read_paginated(entity_type: str):
    async def dependency(
        offset: int | None = Query(None, ge = 0),
        limit: int | None = Query(None, ge = 1, le = 100),
        order: str = Query("asc", pattern = "^(asc|desc)$")
    ):
        return await entity_read(
            query = readEntity(entity = entity_type),
            pagination = queryPagination(offset = offset, limit = limit, order = order)
        )
    return dependency