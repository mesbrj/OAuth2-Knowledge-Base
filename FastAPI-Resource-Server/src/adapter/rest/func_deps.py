
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

    if query.record_id or query.record_name:
        record = await data_manager.process(
            operation = "read",
            entity = query.entity,
            record_id = query.record_id,
            record_name = query.record_name
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