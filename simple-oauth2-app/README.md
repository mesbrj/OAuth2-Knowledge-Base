# Simple OAuth2 App with Hydra & GitHub

A minimal OAuth2 Authorization Code Flow implementation using:
- **Ory Hydra** as the OAuth2 Authorization Server
- **GitHub** for user authentication
- **Pure JavaScript** (no SDK) for the client

## Architecture

```
User Browser -> JavaScript App -> Hydra OAuth2 Server -> Node.js Login/Consent -> GitHub OAuth
```

## Prerequisites

1. **Docker & Docker Compose** installed
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
docker-compose up -d hydra
```

Wait a few seconds for Hydra to start, then create the client:

```bash
docker exec simple-oauth2-app_hydra_1 hydra create oauth2-client \
  --endpoint http://localhost:4445 \
  --name "demo-client" \
  --grant-type authorization_code,refresh_token \
  --response-type code \
  --scope openid,offline \
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
docker-compose up -d
```

## Usage

1. Open http://localhost:3000
2. Click **"Login with GitHub"**
3. You'll be redirected to GitHub to authorize
4. After authorization, you'll see your user info

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

### 3. Consent Flow
```
Hydra -> http://localhost:3000/consent (with consent_challenge)
-> Auto-accepts consent
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

## Project Structure

```
simple-oauth2-app/
├── docker-compose.yml       # Hydra + Node.js app
├── server.js               # Login/Consent handler
├── package.json            # Node.js dependencies
├── .env                    # GitHub credentials (create from .env.example)
└── public/
    ├── index.html         # Main page
    ├── callback.html      # OAuth callback page
    └── app.js            # OAuth2 client logic
```

## Key Files

### `server.js`
Handles Hydra's login and consent flows by:
- Serving OAuth2 client configuration via `/config.js` endpoint
- Redirecting to GitHub for authentication
- Processing GitHub OAuth callback
- Accepting Hydra login/consent challenges

### `public/app.js`
Implements OAuth2 Authorization Code Flow with PKCE:
- Loads OAuth2 client ID from server configuration
- Generates state and PKCE parameters
- Redirects to Hydra authorization endpoint
- Exchanges code for tokens
- Fetches user info

## Configuration

### Environment Variables

Configuration can be set in `.env` file or as system environment variables:

**GitHub OAuth** (required):
- `GITHUB_CLIENT_ID` - Your GitHub OAuth App Client ID
- `GITHUB_CLIENT_SECRET` - Your GitHub OAuth App Client Secret

**OAuth2 Client** (required):
- `OAUTH2_CLIENT_ID` - OAuth2 client ID from Hydra (obtained during client creation)

**Server** (optional):
- `PORT` - Server port (default: 3000)
- `HYDRA_ADMIN_URL` - Hydra admin URL (default: http://hydra:4445 in Docker)
- `NODE_ENV` - Environment (development/production)

### Docker Compose

The `docker-compose.yml` automatically passes environment variables from your host system to the containers:
```yaml
environment:
  - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
  - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
  - OAUTH2_CLIENT_ID=${OAUTH2_CLIENT_ID}
```

This means you can either:
1. Use a `.env` file (recommended for development)
2. Set system environment variables (recommended for production)

### Application URLs

**Hydra** (docker-compose.yml):
- Public URL: `http://localhost:4444`
- Admin URL: `http://localhost:4445`
- Login URL: `http://localhost:3000/login`
- Consent URL: `http://localhost:3000/consent`

**OAuth2 Client** (loaded from environment):
- Client ID: Set via `OAUTH2_CLIENT_ID` in `.env` file
- Redirect URI: `http://localhost:3000/callback`
- Scope: `openid offline`
- Config Endpoint: `http://localhost:3000/config.js` (serves client ID to browser)

**GitHub OAuth** (.env file):
- Set via `GITHUB_CLIENT_ID` environment variable
- Set via `GITHUB_CLIENT_SECRET` environment variable
- Callback URL: `http://localhost:3000/github-callback`

## Troubleshooting

### Hydra not starting
```bash
docker-compose logs hydra
```

### Missing OAUTH2_CLIENT_ID error
If the server fails to start with "OAUTH2_CLIENT_ID must be set" error:
1. Make sure you've created the OAuth2 client in Hydra (see "Create OAuth2 Client" section)
2. Add the `client_id` to your `.env` file as `OAUTH2_CLIENT_ID=your-client-id`
3. Restart the app container: `docker-compose restart app`

### GitHub authentication fails
- Check `.env` file exists and has correct credentials
- Verify `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `OAUTH2_CLIENT_ID` are set
- Verify callback URL matches GitHub app settings: `http://localhost:3000/github-callback`

### Environment variables not loading
```bash
# Check if .env file exists
ls -la .env

# Verify all required variables are set
cat .env

# Verify docker-compose picks up the variables
docker-compose config | grep GITHUB
```

## Stopping

```bash
docker-compose down
```

## Notes

- This is a **development example** - not production-ready
- Uses in-memory storage (data lost on restart)
- GitHub Client Secret is in code (should use environment variable)
- Auto-accepts consent (should show consent UI in production)
- No error handling UI (errors shown as alerts)
