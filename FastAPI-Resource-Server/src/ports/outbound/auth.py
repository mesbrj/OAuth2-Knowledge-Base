from abc import ABC, abstractmethod
from typing import List

from ports.models.auth import TokenData, UserInfo

class PermissionChecker(ABC):
    """
    Port interface for checking user permissions.
    
    Implementations might use Keto, Casbin, or any other
    permission management system.
    """
    
    @abstractmethod
    async def check_permission(self, username: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            username: The username to check
            permission: The permission to verify (e.g., "data:read")
            
        Returns:
            True if user has the permission, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_user_permissions(self, username: str) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            username: The username to query
            
        Returns:
            List of permission strings
        """
        ...
    
    @abstractmethod
    async def get_user_roles(self, username: str) -> List[str]:
        """
        Get all roles assigned to a user.
        
        Args:
            username: The username to query
            
        Returns:
            List of role names
        """
        ...


class TokenValidator(ABC):
    """
    Port interface for token validation and introspection.
    
    Implementations might use Hydra, Auth0, or custom JWT validation.
    """
    
    @abstractmethod
    async def introspect_token(self, token: str) -> TokenData:
        """
        Validate and introspect an access token.
        
        Args:
            token: The access token to validate
            
        Returns:
            TokenData with user information and scopes
            
        Raises:
            ValueError: If token is invalid or expired
        """
        ...


class IdentityProvider(ABC):
    """
    Port interface for OAuth identity providers.
    
    Implementations might be GitHub, Google, Azure AD, etc.
    """
    
    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """
        Generate the authorization URL for OAuth flow.
        
        Args:
            state: CSRF protection state parameter
            
        Returns:
            Full authorization URL to redirect user to
        """
        ...
    
    @abstractmethod
    async def exchange_code(self, code: str) -> str:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Access token from the provider
            
        Raises:
            ValueError: If code exchange fails
        """
        ...
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> UserInfo:
        """
        Fetch user information from the provider.
        
        Args:
            access_token: Valid access token
            
        Returns:
            UserInfo with user details
            
        Raises:
            ValueError: If token is invalid or request fails
        """
        ...
