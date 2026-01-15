from ports.interfaces import dataManager, dbAccess
from adapter.sql.data_access import dbAccessImpl
from core.use_cases import dataManagerImpl, publicCrud


class DependencyContainer:
    def __init__(self):
        self._db_access: dbAccess | None = None
        self._data_manager: dataManager | None = None
        self._public_crud: dataManager | None = None
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._db_access = dbAccessImpl()
        self._data_manager = dataManagerImpl(repository=self._db_access)
        self._public_crud = publicCrud(data_manager=self._data_manager)
        self._initialized = True

    def reset(self) -> None:
        self._db_access = None
        self._data_manager = None
        self._public_crud = None
        self._initialized = False

    def get_db_access(self) -> dbAccess:
        if self._db_access is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._db_access

    def get_data_manager(self) -> dataManager:
        if self._data_manager is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._data_manager

    def get_public_crud(self) -> dataManager:
        if self._public_crud is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._public_crud


container = DependencyContainer()
