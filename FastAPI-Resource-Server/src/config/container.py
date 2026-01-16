from ports.interfaces import DataManager, DbAccess
from ports.auth_interfaces import PermissionChecker, AuthorizationUseCase
from adapter.sql.data_access import DbAccessImpl
from auth.keto_client import keto_permission_checker
from core.use_cases import DataManagerImpl, PublicCrud
from core.auth_use_cases import AuthorizationUseCaseImpl


class DependencyContainer:
    def __init__(self):
        self._db_access: DbAccess | None = None
        self._data_manager: DataManager | None = None
        self._public_crud: DataManager | None = None
        self._permission_checker: PermissionChecker | None = None
        self._authorization_use_case: AuthorizationUseCase | None = None
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        # Data layer
        self._db_access = DbAccessImpl()
        self._data_manager = DataManagerImpl(repository=self._db_access)
        self._public_crud = PublicCrud(data_manager=self._data_manager)
        
        # Auth layer
        self._permission_checker = keto_permission_checker
        self._authorization_use_case = AuthorizationUseCaseImpl(
            permission_checker=self._permission_checker
        )
        
        self._initialized = True

    def reset(self) -> None:
        self._db_access = None
        self._data_manager = None
        self._public_crud = None
        self._permission_checker = None
        self._authorization_use_case = None
        self._initialized = False

    def get_db_access(self) -> DbAccess:
        if self._db_access is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._db_access

    def get_data_manager(self) -> DataManager:
        if self._data_manager is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._data_manager

    def get_public_crud(self) -> DataManager:
        if self._public_crud is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._public_crud

    def get_permission_checker(self) -> PermissionChecker:
        if self._permission_checker is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._permission_checker

    def get_authorization_use_case(self) -> AuthorizationUseCase:
        if self._authorization_use_case is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._authorization_use_case


container = DependencyContainer()
