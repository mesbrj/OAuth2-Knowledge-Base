from abc import ABC, abstractmethod
from typing import List

from ports.models.auth import TokenData, UserInfo

class Authentication(ABC):
    """
    Port interface for authentication use cases.
    
    This represents the application's authentication operations
    that can be triggered from adapters (REST API, CLI, etc.).
    """
    
    @abstractmethod
    async def authenticate_with_provider(
        self, 
        provider_code: str, 
        state: str
    ) -> UserInfo:
        """
        Authenticate user with external identity provider.
        
        Args:
            provider_code: Authorization code from provider
            state: State parameter for CSRF protection
            
        Returns:
            UserInfo of authenticated user
        """
        ...
    
    @abstractmethod
    async def validate_access_token(self, token: str) -> TokenData:
        """
        Validate an access token.
        
        Args:
            token: Access token to validate
            
        Returns:
            TokenData with user and scope information
        """
        ...


class Authorization(ABC):
    """
    Port interface for authorization use cases.
    
    This represents the application's authorization operations.
    """
    
    @abstractmethod
    async def check_user_access(
        self, 
        username: str, 
        required_permission: str
    ) -> bool:
        """
        Check if user has required permission.
        
        Args:
            username: Username to check
            required_permission: Required permission
            
        Returns:
            True if user has permission
        """
        ...
    
    @abstractmethod
    async def get_user_authorized_scopes(
        self, 
        username: str, 
        requested_scopes: List[str]
    ) -> List[str]:
        """
        Filter requested scopes based on user's permissions.
        
        Args:
            username: Username to check
            requested_scopes: Scopes requested by client
            
        Returns:
            List of scopes the user is authorized for
        """
        ...
