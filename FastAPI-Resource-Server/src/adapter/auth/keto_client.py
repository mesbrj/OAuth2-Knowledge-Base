"""
Keto adapter for permission checking (hexagonal architecture).

This adapter implements the PermissionChecker port interface using Ory Keto
as the concrete permission management system.
"""

from typing import List
import httpx
from config.settings import settings
from config.logger import logger
from ports.outbound.auth import PermissionChecker


class KetoPermissionChecker(PermissionChecker):
    """
    Adapter that implements PermissionChecker using Ory Keto.
    
    Keto manages permissions using relation tuples in the format:
    namespace:object#relation@subject
    
    Example:
    - "fastapi-resource-server:data:read#granted@Soro-Kan"
    - "fastapi-resource-server:role:data:admin#member@Soro-Kan"
    """
    
    def __init__(self):
        self.read_url = settings.KETO_READ_URL
        self.write_url = settings.KETO_WRITE_URL
        self.namespace = settings.KETO_NAMESPACE

    async def get_user_permissions(self, username: str) -> List[str]:
        """
        Get all permissions granted to a user from Keto.

        This checks both:
        - Direct permission grants
        - Permissions inherited from roles

        Args:
            username: The username to check permissions for

        Returns:
            List of permission strings (e.g., ["data:read", "data:write"])

        Example:
            permissions = await keto_client.get_user_permissions("Soro-Kan")
            # Returns: ["data:read", "data:write", "data:update", "data:delete"]
        """
        permissions = set()

        try:
            async with httpx.AsyncClient() as client:
                # Query all relation tuples for this user
                # Format: GET /relation-tuples?namespace=X&subject_id=username
                response = await client.get(
                    f"{self.read_url}/relation-tuples",
                    params={
                        "namespace": self.namespace,
                        "subject_id": username
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    relation_tuples = data.get("relation_tuples", [])

                    for tuple_data in relation_tuples:
                        # Extract permission from object field
                        # Example: "data:read" or "role:data:admin"
                        obj = tuple_data.get("object", "")
                        relation = tuple_data.get("relation", "")

                        # Direct permissions have relation "granted"
                        if relation == "granted" and not obj.startswith("role:"):
                            permissions.add(obj)

                        # Role memberships - need to expand to permissions
                        if relation == "member" and obj.startswith("role:"):
                            role_name = obj.replace("role:", "")
                            role_permissions = await self._get_role_permissions(role_name)
                            permissions.update(role_permissions)

                    logger.info(f"Retrieved {len(permissions)} permissions for user '{username}'")
                else:
                    logger.warning(
                        f"Failed to fetch permissions for user '{username}': "
                        f"HTTP {response.status_code}"
                    )

        except httpx.RequestError as e:
            logger.error(f"Error connecting to Keto: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user permissions: {e}")

        return list(permissions)

    async def _get_role_permissions(self, role_name: str) -> List[str]:
        """
        Get all permissions associated with a specific role.

        Args:
            role_name: The role name (e.g., "data:admin")

        Returns:
            List of permission strings
        """
        permissions = []

        try:
            async with httpx.AsyncClient() as client:
                # Query permissions for this role
                # Format: role:data:admin#granted@<permission>
                response = await client.get(
                    f"{self.read_url}/relation-tuples",
                    params={
                        "namespace": self.namespace,
                        "object": f"role:{role_name}",
                        "relation": "granted"
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    relation_tuples = data.get("relation_tuples", [])

                    for tuple_data in relation_tuples:
                        # Extract permission from subject
                        subject = tuple_data.get("subject_id", "")
                        if subject:
                            permissions.append(subject)

        except httpx.RequestError as e:
            logger.error(f"Error fetching role permissions: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting role permissions: {e}")

        return permissions

    async def check_permission(self, username: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        This performs a Keto check query to determine if the user
        has the permission either directly or through a role.

        Args:
            username: The username to check
            permission: The permission to check (e.g., "data:read")

        Returns:
            True if user has the permission, False otherwise

        Example:
            has_access = await keto_client.check_permission("Soro-Kan", "data:read")
            if has_access:
                # User can read data
        """
        try:
            async with httpx.AsyncClient() as client:
                # Use Keto's check API
                # GET /relation-tuples/check?namespace=X&object=Y&relation=granted&subject_id=Z
                response = await client.get(
                    f"{self.read_url}/relation-tuples/check",
                    params={
                        "namespace": self.namespace,
                        "object": permission,
                        "relation": "granted",
                        "subject_id": username
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    allowed = data.get("allowed", False)
                    logger.debug(
                        f"Permission check: user='{username}', permission='{permission}', "
                        f"allowed={allowed}"
                    )
                    return allowed
                else:
                    logger.warning(
                        f"Keto check returned HTTP {response.status_code} "
                        f"for user '{username}' permission '{permission}'"
                    )
                    return False

        except httpx.RequestError as e:
            logger.error(f"Error connecting to Keto for permission check: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking permission: {e}")
            return False

    async def get_user_roles(self, username: str) -> List[str]:
        """
        Get all roles assigned to a user.

        Args:
            username: The username to check roles for
            
        Returns:
            List of role names (e.g., ["data:admin", "project:user"])

        Example:
            roles = await keto_client.get_user_roles("Soro-Kan")
            # Returns: ["data:admin", "project:admin"]
        """
        roles = []

        try:
            async with httpx.AsyncClient() as client:
                # Query role memberships
                response = await client.get(
                    f"{self.read_url}/relation-tuples",
                    params={
                        "namespace": self.namespace,
                        "subject_id": username,
                        "relation": "member"
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    relation_tuples = data.get("relation_tuples", [])

                    for tuple_data in relation_tuples:
                        obj = tuple_data.get("object", "")
                        if obj.startswith("role:"):
                            role_name = obj.replace("role:", "")
                            roles.append(role_name)

                    logger.info(f"Retrieved {len(roles)} roles for user '{username}'")

        except httpx.RequestError as e:
            logger.error(f"Error connecting to Keto: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user roles: {e}")

        return roles


# Singleton instance for convenient access
keto_permission_checker = KetoPermissionChecker()
