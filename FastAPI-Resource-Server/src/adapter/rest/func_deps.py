
from ports.inbound import inbound_factory
from adapter.rest.dto import createUser, createTeam, createResponse


async def entityCreate(body: createUser | createTeam) -> createResponse:
    data_manager = inbound_factory("data")
    new_rec = await data_manager.process(
        operation="create",
        entity=body.entity,
        **body.model_dump(exclude={"entity"})
    )

    return createResponse(
        record_id=new_rec.id,
        record_name=new_rec.name,
        entity=body.entity
        )