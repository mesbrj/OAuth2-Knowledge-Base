#!/bin/bash

USERNAME=$1
KETO_READ_URL="http://localhost:4466"
NAMESPACE="simple-oauth2-app"

if [ -z "$USERNAME" ]; then
  echo "Usage: ./check-permissions.sh <github-username>"
  echo "Example: ./check-permissions.sh github-user-example"
  exit 1
fi

echo "Checking permissions for user: $USERNAME"
echo ""

# Get all relation tuples for this user
echo "Fetching all permissions from Keto..."
RESPONSE=$(curl -s "$KETO_READ_URL/relation-tuples?namespace=$NAMESPACE&subject_id=$USERNAME")

echo "$RESPONSE" | jq '.'

echo ""
echo "Permissions summary:"
echo "$RESPONSE" | jq -r '.relation_tuples[] | "  - \(.relation) on \(.object)"'
