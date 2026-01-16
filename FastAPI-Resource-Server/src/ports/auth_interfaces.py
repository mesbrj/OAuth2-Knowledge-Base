"""
Port interfaces for authentication and authorization.

These interfaces define the contracts for authentication and authorization
operations without specifying implementation details (hexagonal architecture).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


# ===== Domain Models =====

class TokenData(BaseModel):
    """Domain model for validated token information."""
    sub: str  # Subject (user ID)
    username: str
    scopes: List[str]
    active: bool
    expires_at: Optional[int] = None


class UserInfo(BaseModel):
    """Domain model for user identity information."""
    id: str
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# ===== Outbound Ports (Dependencies) =====

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


# ===== Inbound Ports (Use Case Interfaces) =====

class AuthenticationUseCase(ABC):
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


class AuthorizationUseCase(ABC):
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
