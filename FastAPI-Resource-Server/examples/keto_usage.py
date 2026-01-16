"""
Example usage of the Keto permission checker adapter.

This demonstrates how to use the KetoPermissionChecker to check user permissions
and roles in the FastAPI Resource Server.
"""

import asyncio
from auth import keto_permission_checker


async def main():
    """Demonstrate Keto permission checker usage."""
    
    # Example 1: Check if a user has a specific permission
    print("=" * 60)
    print("Example 1: Check specific permission")
    print("=" * 60)
    
    username = "Soro-Kan"
    permission = "data:read"
    
    has_permission = await keto_permission_checker.check_permission(username, permission)
    print(f"User '{username}' has permission '{permission}': {has_permission}")
    
    # Example 2: Get all permissions for a user
    print("\n" + "=" * 60)
    print("Example 2: Get all user permissions")
    print("=" * 60)
    
    permissions = await keto_permission_checker.get_user_permissions(username)
    print(f"User '{username}' has {len(permissions)} permissions:")
    for perm in permissions:
        print(f"  - {perm}")
    
    # Example 3: Get user roles
    print("\n" + "=" * 60)
    print("Example 3: Get user roles")
    print("=" * 60)
    
    roles = await keto_permission_checker.get_user_roles(username)
    print(f"User '{username}' has {len(roles)} roles:")
    for role in roles:
        print(f"  - {role}")
    
    # Example 4: Check multiple permissions
    print("\n" + "=" * 60)
    print("Example 4: Check multiple permissions")
    print("=" * 60)
    
    permissions_to_check = ["data:read", "data:write", "data:delete", "project:read"]
    
    for perm in permissions_to_check:
        allowed = await keto_permission_checker.check_permission(username, perm)
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"  {status}: {perm}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Keto Permission Checker - Usage Examples")
    print("=" * 60)
    print("\nNOTE: This example requires:")
    print("  1. Keto server running on http://localhost:4466")
    print("  2. Permissions loaded (see ory/keto/load-permissions.sh)")
    print("=" * 60 + "\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nMake sure Keto is running and permissions are loaded!")
