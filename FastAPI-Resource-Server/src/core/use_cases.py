from ports.interfaces import dataManager
from ports.repository import repo_factory
from core.data_domain import userEntity

class dataManagerImpl(dataManager):
    """
    Data management operations in all models: Business, Persistence ...
    """
    def __init__(self):
        self.db = repo_factory("database")
        self.entities = {
            "users": userEntity,
        }

    async def process(self, operation: str, entity: str, **kwargs):
        if entity not in self.entities.keys():
            raise ValueError(f"Entity '{entity}' is not supported.")

        if operation == "create":
            attributes = self.entities[entity](**kwargs)
            await self.db.create_record(table_id = entity, attributes = attributes.model_dump())

class publicCrud():
    """
    Proxy class to filter allowed operations and allowed models (only Database)
    """
    def __init__(self):
        self._proxy_to = dataManagerImpl()

    def __getattr__(self, name):
        async def filter(*args, **kwargs):
            if kwargs["model"] not in ["users", "teams", "projects"]:
                return None
            if kwargs["operation"] not in ["create", "read", "update", "delete"]:
                return None
            return await getattr(self._proxy_to, name)(*args, **kwargs)
        return filter
