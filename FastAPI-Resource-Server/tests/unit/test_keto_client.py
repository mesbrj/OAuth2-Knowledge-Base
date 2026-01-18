"""
Unit tests for Keto permission checker adapter.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx

from adapter.auth.keto_client import KetoPermissionChecker


@pytest.fixture
def keto_client():
    """Create a KetoPermissionChecker instance for testing."""
    return KetoPermissionChecker()


@pytest.fixture
def mock_keto_response_direct_permissions():
    """Mock Keto response with direct permissions."""
    return {
        "relation_tuples": [
            {
                "namespace": "fastapi-resource-server",
                "object": "data:read",
                "relation": "granted",
                "subject_id": "testuser"
            },
            {
                "namespace": "fastapi-resource-server",
                "object": "data:write",
                "relation": "granted",
                "subject_id": "testuser"
            }
        ]
    }


@pytest.fixture
def mock_keto_response_role_membership():
    """Mock Keto response with role membership."""
    return {
        "relation_tuples": [
            {
                "namespace": "fastapi-resource-server",
                "object": "role:data:admin",
                "relation": "member",
                "subject_id": "testuser"
            }
        ]
    }


@pytest.fixture
def mock_keto_response_role_permissions():
    """Mock Keto response with role permissions."""
    return {
        "relation_tuples": [
            {
                "namespace": "fastapi-resource-server",
                "object": "role:data:admin",
                "relation": "granted",
                "subject_id": "data:read"
            },
            {
                "namespace": "fastapi-resource-server",
                "object": "role:data:admin",
                "relation": "granted",
                "subject_id": "data:write"
            },
            {
                "namespace": "fastapi-resource-server",
                "object": "role:data:admin",
                "relation": "granted",
                "subject_id": "data:delete"
            }
        ]
    }


@pytest.fixture
def mock_keto_check_allowed():
    """Mock Keto check response - permission allowed."""
    return {"allowed": True}


@pytest.fixture
def mock_keto_check_denied():
    """Mock Keto check response - permission denied."""
    return {"allowed": False}


@pytest.mark.asyncio
async def test_get_user_permissions_direct(
    keto_client, 
    mock_keto_response_direct_permissions
):
    """Test getting direct permissions for a user."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_keto_response_direct_permissions
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        permissions = await keto_client.get_user_permissions("testuser")
        
        # Verify
        assert len(permissions) == 2
        assert "data:read" in permissions
        assert "data:write" in permissions


@pytest.mark.asyncio
async def test_get_user_permissions_with_roles(
    keto_client,
    mock_keto_response_role_membership,
    mock_keto_response_role_permissions
):
    """Test getting permissions through role membership."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock to return different responses for different calls
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        # First call: get user's role memberships
        # Second call: get role permissions
        responses = []
        
        # User role membership response
        role_response = Mock()
        role_response.status_code = 200
        role_response.json.return_value = mock_keto_response_role_membership
        responses.append(role_response)
        
        # Role permissions response
        perm_response = Mock()
        perm_response.status_code = 200
        perm_response.json.return_value = mock_keto_response_role_permissions
        responses.append(perm_response)
        
        mock_client_instance.get = AsyncMock(side_effect=responses)
        mock_client.return_value = mock_client_instance
        
        # Execute
        permissions = await keto_client.get_user_permissions("testuser")
        
        # Verify - should have permissions from the role
        assert len(permissions) >= 1
        assert any(p in ["data:read", "data:write", "data:delete"] for p in permissions)


@pytest.mark.asyncio
async def test_check_permission_allowed(keto_client, mock_keto_check_allowed):
    """Test permission check when permission is allowed."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_keto_check_allowed
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        allowed = await keto_client.check_permission("testuser", "data:read")
        
        # Verify
        assert allowed is True


@pytest.mark.asyncio
async def test_check_permission_denied(keto_client, mock_keto_check_denied):
    """Test permission check when permission is denied."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_keto_check_denied
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        allowed = await keto_client.check_permission("testuser", "data:delete")
        
        # Verify
        assert allowed is False


@pytest.mark.asyncio
async def test_check_permission_keto_error(keto_client):
    """Test permission check when Keto returns an error."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock to return error
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        allowed = await keto_client.check_permission("testuser", "data:read")
        
        # Verify - should return False on error
        assert allowed is False


@pytest.mark.asyncio
async def test_check_permission_connection_error(keto_client):
    """Test permission check when connection to Keto fails."""
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock to raise connection error
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        mock_client.return_value = mock_client_instance
        
        # Execute
        allowed = await keto_client.check_permission("testuser", "data:read")
        
        # Verify - should return False on connection error
        assert allowed is False


@pytest.mark.asyncio
async def test_get_user_roles(keto_client):
    """Test getting user roles."""
    mock_roles_response = {
        "relation_tuples": [
            {
                "namespace": "fastapi-resource-server",
                "object": "role:data:admin",
                "relation": "member",
                "subject_id": "testuser"
            },
            {
                "namespace": "fastapi-resource-server",
                "object": "role:project:user",
                "relation": "member",
                "subject_id": "testuser"
            }
        ]
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_roles_response
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        roles = await keto_client.get_user_roles("testuser")
        
        # Verify
        assert len(roles) == 2
        assert "data:admin" in roles
        assert "project:user" in roles


@pytest.mark.asyncio
async def test_get_user_permissions_empty(keto_client):
    """Test getting permissions for user with no permissions."""
    mock_empty_response = {"relation_tuples": []}
    
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_empty_response
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        # Execute
        permissions = await keto_client.get_user_permissions("testuser")
        
        # Verify
        assert len(permissions) == 0
