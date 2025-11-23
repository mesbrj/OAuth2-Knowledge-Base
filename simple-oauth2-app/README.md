# Simple OAuth2 App with Ory Hydra, Keto & GitHub

A minimal OAuth2 Authorization Code Flow implementation using:
- **Ory Hydra** as the OAuth2 Authorization Server
- **Ory Keto** for RBAC management
- **GitHub** for user authentication
- **Pure JavaScript** (no SDK) for the client

## Architecture

```
User Browser -> JavaScript App -> Ory Hydra (OAuth2) -> Node.js Login/Consent -> Ory Keto (Permissions) + GitHub OAuth
```

**Flow**: User authenticates via GitHub → Hydra manages OAuth2 → Keto filters scopes based on user permissions → Tokens issued with authorized scopes only

## Prerequisites

1. **Podman & Podman-Compose 1.5.0 (better --no-recreate support)** installed
2. **GitHub OAuth App** configured

## GitHub Configuration

1. Go to https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - **Application name**: `Simple OAuth2 App`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/github-callback`
4. Click **"Register application"**
5. Copy your **Client ID** and **Client Secret**

## Installation

```bash
cd simple-oauth2-app

# Create .env file from example
cp .env.example .env

# Edit .env and add your GitHub credentials
# GITHUB_CLIENT_ID=your_client_id_here
# GITHUB_CLIENT_SECRET=your_client_secret_here
```

## Create OAuth2 Client

Before starting the services, create an OAuth2 client in Hydra. First, start only Hydra:

```bash
podman-compose up -d hydra
```

Wait a few seconds for Hydra to start, then create the client:

```bash
podman exec simple-oauth2-app_hydra_1 hydra create oauth2-client \
  --endpoint http://localhost:4445 \
  --name "demo-client" \
  --grant-type authorization_code,refresh_token \
  --response-type code \
  --scope openid,offline,records:read,records:write,records:delete,posts:read,posts:write,admin,users:read \
  --redirect-uri http://localhost:3000/callback \
  --token-endpoint-auth-method none \
  --format json
```

This will output JSON with your `client_id`. **Copy the client_id value** and add it to your `.env` file:

```bash
# Add to .env file
OAUTH2_CLIENT_ID=client_id
```

Now start all services:

```bash
podman-compose up -d --no-recreate keto app
```

Load Keto permissions:

```bash
./load-permissions.sh
```

## Usage

1. Open http://localhost:3000
2. Click **"Login with GitHub"**
3. You'll be redirected to GitHub to authorize
4. After authorization, you'll see your user info and Granted Scopes

## How It Works

### 1. Authorization Request
```javascript
// Client generates PKCE challenge and redirects to Hydra
GET http://localhost:4444/oauth2/auth?
  client_id=demo-client&
  response_type=code&
  redirect_uri=http://localhost:3000/callback&
  scope=openid offline&
  state=random_state&
  code_challenge=challenge&
  code_challenge_method=S256
```

### 2. Login Flow
```
Hydra -> http://localhost:3000/login (with login_challenge)
-> Redirects to GitHub OAuth
-> GitHub authenticates user
-> Callback to /github-callback
-> Accepts Hydra login challenge
-> Returns to Hydra
```

### 3. Consent Flow (with Keto Permission Filtering)
```
Hydra -> http://localhost:3000/consent (with consent_challenge)
-> Server queries Keto for user's permissions:
   GET http://keto:4466/relation-tuples?namespace=simple-oauth2-app&subject_id=username
-> Server filters requested scopes based on Keto permissions
-> Accepts consent with filtered scopes
-> Returns to Hydra
```

### 4. Token Exchange
```javascript
// Client exchanges authorization code for tokens
POST http://localhost:4444/oauth2/token
  grant_type=authorization_code&
  code=auth_code&
  redirect_uri=http://localhost:3000/callback&
  client_id=demo-client&
  code_verifier=verifier
```

### 5. Get User Info
```javascript
// Client fetches user info with access token
GET http://localhost:4444/userinfo
  Authorization: Bearer access_token
```

## Permission Model

### Namespace
- `simple-oauth2-app` - All permissions for this application

### Relations
- `member` - User is a member of a role
- `granted` - Permission is granted to a role/user

### Example Structure
```
User: github-user-example
  ↓ (member)
Role: collector:admin
  ↓ (granted)
Permissions: records:read, records:write, records:delete
```

## Key Files

### `server.js`
Handles Hydra's login and consent flows by:
- Serving OAuth2 client configuration via `/config.js` endpoint
- Redirecting to GitHub for authentication
- Processing GitHub OAuth callback
- **Querying Keto** during consent to get user permissions
- **Filtering requested scopes** based on Keto permissions
- Accepting Hydra login/consent challenges with filtered scopes

### `public/app.js`
Implements OAuth2 Authorization Code Flow with PKCE:
- Loads OAuth2 client ID from server configuration
- Generates state and PKCE parameters
- Redirects to Hydra authorization endpoint with custom scopes
- Exchanges code for tokens
- Fetches user info
- **Displays granted scopes** as colored badges (blue: standard, green: custom)

### `roles-permissions.json`
Defines all roles and permissions:
- Maps users to roles
- Defines role permissions
- Supports direct permission grants
- Loaded into Keto via `./load-permissions.sh`

