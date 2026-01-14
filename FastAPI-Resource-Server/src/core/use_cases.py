from ports.interfaces import dataManager
from ports.repository import repo_factory
from core.data_manager_helper import validation_helper
from core.data_domain import (
    userEntity, teamEntity, projectEntity,
    projectRoleEntity, startedProjectEntity
)


class dataManagerImpl(dataManager):
    """
    Data management operations in all models: Business, Persistence ...
    """
    def __init__(self):
        self.db = repo_factory("database")
        self.entities = {
            "users": userEntity,
            "teams": teamEntity,
            "projects": projectEntity,
            "project_roles": projectRoleEntity,
            "started_projects": startedProjectEntity,
        }

    @validation_helper
    async def process(self, operation: str, entity: str, **kwargs):
        if (
            not entity 
            or entity not in self.entities.keys()
        ):
            raise ValueError(f"Entity '{entity}' is not supported.")

        if operation == "create":
            attributes = self.entities[entity](**kwargs)
            record = await self.db.create_record(
                table_id = entity,
                attributes = attributes.model_dump(exclude_none=True)
            )
            return record

        elif operation == "read":
            record = await self.db.read_record(
                table_id = entity,
                record_name = kwargs.get("record_name", None),
                record_id = kwargs.get("record_id", None),
                offset = kwargs.get("offset", None),
                limit = kwargs.get("limit", None),
                order = kwargs.get("order", "asc"),
            )
            return record

class publicCrud():
    """
    Proxy class to filter allowed operations and allowed models (only Database)
    """
    def __init__(self):
        self._proxy_to = dataManagerImpl()

    def __getattr__(self, name):
        async def filter(*args, **kwargs):
            if kwargs["entity"] not in ["users", "teams", "projects"]:
                return None
            if kwargs["operation"] not in ["create", "read", "update", "delete"]:
                return None
            return await getattr(self._proxy_to, name)(*args, **kwargs)
        return filter
