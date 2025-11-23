#!/bin/bash

echo "Loading roles and permissions into Keto from roles-permissions.json..."

KETO_WRITE_URL="http://localhost:4467"
ROLES_FILE="roles-permissions.json"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install it: sudo apt-get install jq (Debian/Ubuntu) or brew install jq (Mac)"
    exit 1
fi

# Check if roles file exists
if [ ! -f "$ROLES_FILE" ]; then
    echo "Error: $ROLES_FILE not found"
    exit 1
fi

# Wait for Keto to be ready
echo "Waiting for Keto to be ready..."
until curl -s "$KETO_WRITE_URL/health/ready" > /dev/null 2>&1; do
  echo "   Keto not ready yet, waiting..."
  sleep 2
done
echo "Keto is ready!"

# Extract namespace from JSON
NAMESPACE=$(jq -r '.namespace' "$ROLES_FILE")
echo "Namespace: $NAMESPACE"
echo ""

# Step 1: Assign users to roles
echo "Step 1: Assigning users to roles..."
jq -r '.users | to_entries[] | "\(.key) \(.value.roles[])"' "$ROLES_FILE" | while read -r username role; do
    echo " → Assigning '$role' to '$username'"
    curl -s -X PUT "$KETO_WRITE_URL/admin/relation-tuples" \
      -H "Content-Type: application/json" \
      -d "{
        \"namespace\": \"$NAMESPACE\",
        \"object\": \"$role\",
        \"relation\": \"member\",
        \"subject_id\": \"$username\"
      }" > /dev/null
done

# Step 2: Assign direct permissions to users (if any)
echo ""
echo "Step 2: Assigning direct permissions to users..."
jq -r '.users | to_entries[] | select(.value.direct_permissions | length > 0) | "\(.key) \(.value.direct_permissions[])"' "$ROLES_FILE" | while read -r username permission; do
    echo " → Granting '$permission' directly to '$username'"
    curl -s -X PUT "$KETO_WRITE_URL/admin/relation-tuples" \
      -H "Content-Type: application/json" \
      -d "{
        \"namespace\": \"$NAMESPACE\",
        \"object\": \"$permission\",
        \"relation\": \"granted\",
        \"subject_id\": \"$username\"
      }" > /dev/null
done

# Step 3: Assign permissions to roles
echo ""
echo "Step 3: Granting permissions to roles..."
jq -r '.roles | to_entries[] | "\(.key) \(.value.permissions[])"' "$ROLES_FILE" | while read -r role permission; do
    echo " → Granting '$permission' to role '$role'"
    curl -s -X PUT "$KETO_WRITE_URL/admin/relation-tuples" \
      -H "Content-Type: application/json" \
      -d "{
        \"namespace\": \"$NAMESPACE\",
        \"object\": \"$permission\",
        \"relation\": \"granted\",
        \"subject_set\": {
          \"namespace\": \"$NAMESPACE\",
          \"object\": \"$role\",
          \"relation\": \"member\"
        }
      }" > /dev/null
done

echo ""
echo "All permissions loaded successfully!"
echo ""
echo "Summary:"
echo " - Namespace: $NAMESPACE"
echo " - Roles: $(jq -r '.roles | keys[]' "$ROLES_FILE" | wc -l) defined"
echo " - Users: $(jq -r '.users | keys[]' "$ROLES_FILE" | wc -l) configured"
echo ""
echo "Verify permissions for a user:"
echo " ./check-permissions.sh <github-username>"
echo ""
echo "View all tuples:"
echo " curl http://localhost:4466/relation-tuples?namespace=$NAMESPACE | jq '.'"
