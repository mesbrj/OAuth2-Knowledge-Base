"""
Unit tests for authentication and authorization use cases.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from core.auth.use_cases import AuthorizationImpl
from ports.outbound.auth import PermissionChecker


@pytest.fixture
def mock_permission_checker():
    """Create a mock PermissionChecker."""
    mock = Mock(spec=PermissionChecker)
    return mock


@pytest.fixture
def authorization_use_case(mock_permission_checker):
    """Create an AuthorizationImpl with mock dependencies."""
    return AuthorizationImpl(mock_permission_checker)


@pytest.mark.asyncio
async def test_check_user_access_allowed(authorization_use_case, mock_permission_checker):
    """Test check_user_access when permission is granted."""
    # Setup
    mock_permission_checker.check_permission = AsyncMock(return_value=True)
    
    # Execute
    result = await authorization_use_case.check_user_access("testuser", "data:read")
    
    # Verify
    assert result is True
    mock_permission_checker.check_permission.assert_called_once_with(
        "testuser", "data:read"
    )


@pytest.mark.asyncio
async def test_check_user_access_denied(authorization_use_case, mock_permission_checker):
    """Test check_user_access when permission is denied."""
    # Setup
    mock_permission_checker.check_permission = AsyncMock(return_value=False)
    
    # Execute
    result = await authorization_use_case.check_user_access("testuser", "data:delete")
    
    # Verify
    assert result is False
    mock_permission_checker.check_permission.assert_called_once_with(
        "testuser", "data:delete"
    )


@pytest.mark.asyncio
async def test_check_user_access_error_handling(authorization_use_case, mock_permission_checker):
    """Test check_user_access handles errors gracefully (fail-safe)."""
    # Setup - make permission check raise an exception
    mock_permission_checker.check_permission = AsyncMock(
        side_effect=Exception("Connection error")
    )
    
    # Execute
    result = await authorization_use_case.check_user_access("testuser", "data:read")
    
    # Verify - should return False on error (fail-safe)
    assert result is False


@pytest.mark.asyncio
async def test_get_user_authorized_scopes_all_authorized(
    authorization_use_case, 
    mock_permission_checker
):
    """Test filtering scopes when user has all requested permissions."""
    # Setup
    requested_scopes = ["data:read", "data:write"]
    user_permissions = ["data:read", "data:write", "data:delete"]
    
    mock_permission_checker.get_user_permissions = AsyncMock(
        return_value=user_permissions
    )
    
    # Execute
    result = await authorization_use_case.get_user_authorized_scopes(
        "testuser", 
        requested_scopes
    )
    
    # Verify
    assert len(result) == 2
    assert "data:read" in result
    assert "data:write" in result


@pytest.mark.asyncio
async def test_get_user_authorized_scopes_partial_authorization(
    authorization_use_case,
    mock_permission_checker
):
    """Test filtering scopes when user has only some permissions."""
    # Setup
    requested_scopes = ["data:read", "data:write", "data:delete"]
    user_permissions = ["data:read"]  # User only has read permission
    
    mock_permission_checker.get_user_permissions = AsyncMock(
        return_value=user_permissions
    )
    
    # Execute
    result = await authorization_use_case.get_user_authorized_scopes(
        "testuser",
        requested_scopes
    )
    
    # Verify - should only get data:read
    assert len(result) == 1
    assert "data:read" in result
    assert "data:write" not in result
    assert "data:delete" not in result


@pytest.mark.asyncio
async def test_get_user_authorized_scopes_no_permissions(
    authorization_use_case,
    mock_permission_checker
):
    """Test filtering scopes when user has no permissions."""
    # Setup
    requested_scopes = ["data:read", "data:write"]
    user_permissions = []  # User has no permissions
    
    mock_permission_checker.get_user_permissions = AsyncMock(
        return_value=user_permissions
    )
    
    # Execute
    result = await authorization_use_case.get_user_authorized_scopes(
        "testuser",
        requested_scopes
    )
    
    # Verify - should get empty list
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_user_authorized_scopes_error_handling(
    authorization_use_case,
    mock_permission_checker
):
    """Test scope filtering handles errors gracefully (fail-safe)."""
    # Setup - make get_user_permissions raise an exception
    mock_permission_checker.get_user_permissions = AsyncMock(
        side_effect=Exception("Connection error")
    )
    
    # Execute
    result = await authorization_use_case.get_user_authorized_scopes(
        "testuser",
        ["data:read", "data:write"]
    )
    
    # Verify - should return empty list on error (fail-safe)
    assert len(result) == 0
