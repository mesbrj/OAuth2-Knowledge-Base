"""
Authentication and authorization module.

This module handles:
- OAuth2 token validation and introspection
- GitHub OAuth provider integration
- Keto permission checking
- FastAPI security dependencies
"""

from auth.keto_client import KetoPermissionChecker, keto_permission_checker

__all__ = [
    "KetoPermissionChecker",
    "keto_permission_checker",
]
