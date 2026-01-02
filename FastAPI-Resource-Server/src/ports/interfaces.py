from uuid import UUID
from abc import ABC, abstractmethod

# inbound interfaces

class dataManager(ABC):
    """
    Interface for data management operations in all models: Business, Persistence ...
    """
    @abstractmethod
    async def process(self, operation: str, entity: str, **kwargs): ...

# repository interfaces

class dbAccess(ABC):
    """
    Interface for database operations
    """
    @abstractmethod
    async def create_record(self, table_id: str, attributes: dict): ...

    @abstractmethod
    async def read_record(
        self, table_id: str, record_name: str | None = None, record_id: UUID | None = None
        ): ...

#    @abstractmethod
#    async def update(self, table_id: str, attributes: dict): ...

