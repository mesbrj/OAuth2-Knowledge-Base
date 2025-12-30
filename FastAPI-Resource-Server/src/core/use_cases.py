from ports.interfaces import dataManager
from ports.repository import repo_factory

class dataManagerImpl(dataManager):
    """
    Data management operations in all models: Business, Persistence ...
    """
    def __init__(self):
        self.db = repo_factory("database")

    async def process(self, operation: str, model: str, **kwargs):
        if operation == "create":
            await self.db.create(model, **kwargs)

class publicCrud(object):
    """
    Proxy class to filter allowed operations and allowed models (only Database)
    """
    def __init__(self):
        self._proxy_to = dataManagerImpl()

    def __getattr__(self, name):
        def filter(*args, **kwargs):
            if kwargs["model"] not in ["users", "teams", "projects"]:
                return None
            if kwargs["operation"] not in ["create", "read", "update", "delete"]:
                return None
            return getattr(self._proxy_to, name)(*args, **kwargs)
        return filter
