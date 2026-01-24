# OAuth2 Authorization Code Flow - Implementation Plan

## Project Overview

This document outlines the complete implementation plan for adding OAuth2 Authorization Code flow with GitHub authentication and Ory Keto permission management to the FastAPI Resource Server.

### Architecture Summary

- **FastAPI Backend**: Handles both auth flow and protected API endpoints
- **Ory Hydra**: OAuth2 authorization server (issues tokens)
- **GitHub OAuth**: Social authentication provider
- **Ory Keto**: Permission/scope management system
- **Token Type**: Opaque tokens (validated via introspection)
- **Client Type**: Confidential (PKCE + client_secret)

**Hexagonal Architecture (Ports & Adapters):**
- **Core Layer** (`src/core/`): Business logic independent of external systems
  - `auth/use_cases.py`: Authentication and authorization use cases
  - `data_manager/use_cases.py`: Data management use cases
- **Ports Layer** (`src/ports/`): Interface contracts
  - `inbound/`: Use case interfaces (entry points to core)
  - `outbound/`: Adapter interfaces (external dependencies)
  - `models/`: Models (stable contracts)
  - `repository/`: Database interfaces
- **Adapters Layer** (`src/adapter/`): External system implementations
  - `auth/`: Authentication adapters (Keto, Hydra, GitHub)
  - `rest/`: FastAPI REST API
  - `sql/`: Database layer (SQLAlchemy)
- **Config Layer** (`src/config/`): Dependency injection and settings

### Use Case

This is an **API-first authentication system** where:
- Users authenticate via browser (GitHub OAuth)
- Receive a one-time access token
- Use token with CLI tools (curl, wget, Postman) to access protected API endpoints
- No complex frontend application needed

---

## Implementation Phases

### 📋 Phase 1: Project Setup & Dependencies

**Goal:** Prepare the project foundation and install required packages

**Tasks:**
1. Update `requirements.txt` with new dependencies
2. Create environment configuration file (`.env.example`)
3. Create/update `src/config/settings.py` with OAuth2 settings
4. Install dependencies
5. Create project structure for new modules

**Deliverables:**
- Updated `requirements.txt`
- `.env.example` file
- Updated `settings.py` with all OAuth2 configurations
- New directories:
  - `src/adapter/auth/` - Authentication adapters (Keto, Hydra, GitHub)
  - `src/ports/inbound/` - Use case interfaces
  - `src/ports/outbound/` - Adapter interfaces
  - `src/ports/models/` - Auth models
  - `src/core/auth/` - Authentication/authorization use cases
  - `static/` - Frontend assets

**New Dependencies:**
```
httpx                          # HTTP client for API calls
authlib                        # OAuth2 client library
python-multipart               # Form data handling
pydantic-settings             # Settings management
```

**Testing:** 
```bash
# Verify imports work
python -c "import httpx, authlib"
# Verify settings load
python -c "from config.settings import Settings; print(Settings())"
```

---

### 📋 Phase 2: Keto Integration

**Goal:** Implement permission checking with Ory Keto following hexagonal architecture

**Tasks:**
1. Create port interface: `src/ports/outbound/auth.py` with `PermissionChecker` ABC
2. Create adapter: `src/adapter/auth/keto_client.py` implementing `PermissionChecker`
3. Create use case: `src/core/auth/use_cases.py` with `AuthorizationImpl`
4. Wire dependencies in `src/config/container.py`
5. Add Keto configuration to settings

**Deliverables:**
- Port interface: `PermissionChecker` (abstraction)
- Adapter: `KetoPermissionChecker` (concrete implementation)
- Use case: `AuthorizationImpl` (business logic)
- Auth models in `src/ports/models/auth.py`

**Key Components:**
```python
# Port (Interface)
class PermissionChecker(ABC):
    async def get_user_permissions(username: str) -> List[str]
    async def check_permission(username: str, permission: str) -> bool
    async def get_user_roles(username: str) -> List[str]

# Adapter (Implementation)
class KetoPermissionChecker(PermissionChecker):
    # Implements all abstract methods using Ory Keto

# Use Case (Business Logic)
class AuthorizationImpl(Authorization):
    def __init__(self, permission_checker: PermissionChecker)
    async def check_user_access(username, permission) -> bool
    async def get_user_authorized_scopes(username, scopes) -> List[str]
```

**Testing:**
```bash
# Test against running Keto instance
curl http://localhost:4466/relation-tuples
# Or use mock for unit tests
```

---

### 📋 Phase 3: GitHub OAuth Provider

**Goal:** Implement GitHub OAuth authentication integration following hexagonal architecture

**Tasks:**
1. Add `IdentityProvider` interface to `src/ports/outbound/auth.py`
2. Create adapter: `src/adapter/auth/github_provider.py` implementing `IdentityProvider`
3. Update use case: `src/core/auth/use_cases.py` with `AuthenticationImpl`
4. Wire into dependency container
5. Add GitHub credentials to settings

**Deliverables:**
- Port interface: `IdentityProvider` (abstraction)
- Adapter: `GitHubIdentityProvider` (concrete implementation)
- Use case: `AuthenticationImpl` (business logic)
- Updated auth models: `UserInfo` in `src/ports/models/auth.py`

**Key Components:**
```python
# Port (Interface)
class IdentityProvider(ABC):
    def get_authorization_url(state: str) -> str
    async def exchange_code(code: str) -> str
    async def get_user_info(access_token: str) -> UserInfo

# Adapter (Implementation)
class GitHubIdentityProvider(IdentityProvider):
    # Implements GitHub OAuth flow

# Use Case (Business Logic)
class AuthenticationImpl(Authentication):
    def __init__(self, identity_provider: IdentityProvider, token_validator: TokenValidator)
    async def authenticate_with_provider(code, state) -> UserInfo
    async def validate_access_token(token) -> TokenData
```

**Testing:**
```python
# Unit tests with mocked GitHub API responses
@pytest.mark.asyncio
async def test_github_user_info():
    # Mock httpx responses
    ...
```

---

### 📋 Phase 4: Token Validation & OAuth2 Dependencies

**Goal:** Implement token introspection and FastAPI dependencies following hexagonal architecture

**Tasks:**
1. Add `TokenValidator` interface to `src/ports/outbound/auth.py`
2. Create `TokenData` model in `src/ports/models/auth.py`
3. Create adapter: `src/adapter/auth/hydra_validator.py` implementing `TokenValidator`
4. Update `AuthenticationImpl` in `src/core/auth/use_cases.py` to use `TokenValidator`
5. Create FastAPI dependencies in `src/adapter/rest/auth_dependencies.py`
6. Add HTTP Bearer security scheme

**Deliverables:**
- Port interface: `TokenValidator` (abstraction)
- Auth model: `TokenData` (in ports/models)
- Adapter: `HydraTokenValidator` (concrete implementation)
- REST layer: FastAPI dependencies for authentication
- Dependency injection wiring

**Key Components:**
```python
# Auth Model (ports/models/auth.py)
class TokenData(BaseModel):
    sub: str
    username: str
    scopes: List[str]
    active: bool
    expires_at: Optional[int]

# Port (Interface - ports/outbound/auth.py)
class TokenValidator(ABC):
    async def introspect_token(token: str) -> TokenData

# Adapter (Implementation - adapter/auth/hydra_validator.py)
class HydraTokenValidator(TokenValidator):
    async def introspect_token(token: str) -> TokenData:
        # Call Hydra introspection endpoint

# Use Case (Updated - core/auth/use_cases.py)
class AuthenticationImpl(Authentication):
    def __init__(self, identity_provider: IdentityProvider, token_validator: TokenValidator)
    async def validate_access_token(token: str) -> TokenData

# FastAPI Dependencies (adapter/rest/auth_dependencies.py)
async def get_current_user(credentials: HTTPAuthorizationCredentials) -> TokenData
def require_scope(required_scope: str) -> Callable
```

**Testing:**
```python
# Unit tests with mocked Hydra introspection responses
@pytest.mark.asyncio
async def test_introspect_valid_token():
    # Mock Hydra response
    ...
```

---

### 📋 Phase 5: Auth Routes - Hydra Flow Handlers

**Goal:** Implement login and consent challenge handlers

**Tasks:**
1. Create `src/adapter/rest/auth_routes.py`
2. Implement core Hydra flow endpoints:
   - `GET /auth/login` - Handle Hydra login challenge
   - `GET /auth/github-callback` - Handle GitHub callback
   - `GET /auth/consent` - Handle Hydra consent challenge (with Keto integration)
3. Wire up GitHub provider and Keto client

**Deliverables:**
- Login flow handler (redirects to GitHub)
- GitHub callback handler (accepts login with Hydra)
- Consent flow handler (checks Keto, grants filtered scopes)

**Route Details:**

| Route | Called By | Purpose |
|-------|-----------|---------|
| `/auth/login` | Hydra | Redirect user to GitHub for authentication |
| `/auth/github-callback` | GitHub | Accept Hydra login with user info |
| `/auth/consent` | Hydra | Check Keto permissions and grant scopes |

**Testing:**
```bash
# Integration test with Hydra + GitHub (or mocked)
curl "http://localhost:8080/auth/login?login_challenge=test123"
```

---

### 📋 Phase 6: Auth Routes - Client Proxy Endpoints

**Goal:** Implement OAuth2 proxy endpoints for clients

**Tasks:**
1. Add to `src/adapter/rest/auth_routes.py`:
   - `GET /auth/authorize` - Proxy to Hydra authorization endpoint
   - `POST /auth/token` - Proxy token exchange (hide client_secret)
   - `GET /auth/userinfo` - Proxy userinfo endpoint
   - `GET /auth/config` - Provide OAuth2 config to frontend
   - `POST /auth/refresh` - Token refresh endpoint *(Enhancement)*
   - `POST /auth/introspect` - Token introspection endpoint *(Enhancement)*

**Deliverables:**
- Complete proxy endpoints
- Client configuration endpoint
- Enhancement endpoints (refresh, introspect)

**Route Details:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/auth/authorize` | GET | Proxy OAuth2 authorization flow start |
| `/auth/token` | POST | Exchange code for token (hides secret) |
| `/auth/userinfo` | GET | Get user information |
| `/auth/config` | GET | Frontend configuration |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/introspect` | POST | Check token validity |

**Testing:**
```bash
# Test token exchange
curl -X POST http://localhost:8080/auth/token \
  -d "grant_type=authorization_code&code=xxx&redirect_uri=..."
```

---

### 📋 Phase 7: Static File Serving & HTML Pages

**Goal:** Create frontend pages for authentication flow

**Tasks:**
1. Update `src/adapter/rest/server.py`:
   - Add static file mounting
   - Add routes to serve HTML pages
2. Create `static/index.html` - Start/login page with "Login with GitHub" button
3. Create `static/callback.html` - Token display page (one-time view)
4. Implement OAuth2 PKCE flow in JavaScript

**Deliverables:**
- Static file serving configuration
- Login page with OAuth2 flow initiation
- Callback page with token display (security: one-time view, no storage)
- JavaScript for PKCE challenge generation

**HTML Pages:**

| Page | Route | Purpose |
|------|-------|---------|
| `index.html` | `/` | Login button, start OAuth2 flow |
| `callback.html` | `/callback` | Display token once, instructions for usage |

**Security Features:**
- PKCE code challenge generation
- State parameter validation (CSRF protection)
- One-time token display (cleared on refresh)
- URL parameter cleanup after token exchange
- Warning before page navigation

**Testing:**
```bash
# Open browser and test flow
firefox http://localhost:8080/
```

---

### 📋 Phase 8: Protect Existing Routes

**Goal:** Add authentication to existing API endpoints

**Tasks:**
1. Update `src/adapter/rest/routes.py`:
   - Import OAuth2 dependencies
   - Add `get_current_user` dependency to all protected routes
   - Add `require_scope()` dependency with appropriate scopes
   - Map CRUD operations to scopes

**Scope Mapping:**

| Operation | HTTP Method | Required Scope |
|-----------|-------------|----------------|
| Read | GET | `data:read` |
| Create | POST | `data:write` |
| Update | PUT/PATCH | `data:update` |
| Delete | DELETE | `data:delete` |

**Deliverables:**
- Protected `/users` endpoints
- Protected `/teams` endpoints
- Scope-based authorization on all routes

**Example:**
```python
@crud_routes.get("/users", dependencies=[Depends(require_scope("data:read"))])
async def read_all_users(...):
    ...

@crud_routes.post("/users", dependencies=[Depends(require_scope("data:write"))])
async def create_user(...):
    ...
```

**Testing:**
```bash
# Test with valid token
curl -H "Authorization: Bearer ory_at_xxx" http://localhost:8080/users

# Test with invalid token (should fail)
curl -H "Authorization: Bearer invalid" http://localhost:8080/users

# Test without required scope (should fail)
curl -H "Authorization: Bearer token_without_write_scope" \
  -X POST http://localhost:8080/users
```

---

### 📋 Phase 9: Docker Compose & Ory Services

**Goal:** Configure Hydra and Keto services

**Tasks:**
1. Update `ory/docker-compose.yml`:
   - Configure Hydra with login/consent URLs pointing to FastAPI
   - Configure Keto with namespace settings
   - Add FastAPI service to docker-compose
   - Set up networking between services
2. Verify Hydra Dockerfile configuration
3. Verify Keto Dockerfile and permissions loading

**Deliverables:**
- Updated `docker-compose.yml`
- Proper service networking
- Environment variables configured

**Key Configuration:**
```yaml
hydra:
  environment:
    - URLS_LOGIN=http://fastapi:8080/auth/login
    - URLS_CONSENT=http://fastapi:8080/auth/consent
    - URLS_SELF_ISSUER=http://localhost:4444

fastapi:
  environment:
    - HYDRA_ADMIN_URL=http://hydra:4445
    - HYDRA_PUBLIC_URL=http://hydra:4444
    - KETO_READ_URL=http://keto:4466
```

**Testing:**
```bash
docker-compose -f ory/docker-compose.yml up
# Verify all services are running
docker-compose ps
```

---

### 📋 Phase 10: Environment Configuration & Secrets

**Goal:** Set up environment variables and secrets

**Tasks:**
1. Create `.env` file (not committed to git)
2. Configure all required environment variables
3. Document environment variables in `.env.example`
4. Add `.env` to `.gitignore`

**Deliverables:**
- `.env` file with all secrets (local only)
- `.env.example` template for documentation

**Required Environment Variables:**
```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8080/auth/github-callback

# Hydra
HYDRA_ADMIN_URL=http://localhost:4445
HYDRA_PUBLIC_URL=http://localhost:4444

# Keto
KETO_READ_URL=http://localhost:4466
KETO_WRITE_URL=http://localhost:4467
KETO_NAMESPACE=fastapi-resource-server

# OAuth2 Client (created in Phase 11)
OAUTH2_CLIENT_ID=your_hydra_client_id
OAUTH2_CLIENT_SECRET=your_hydra_client_secret

# Application
APP_URL=http://localhost:8080
ENVIRONMENT=development
```

**Testing:**
```bash
# Verify environment loads
python -c "from config.settings import Settings; s=Settings(); print(s.GITHUB_CLIENT_ID)"
```

---

### 📋 Phase 11: Hydra Client Registration

**Goal:** Create OAuth2 client in Hydra

**Tasks:**
1. Start Hydra service
2. Run Hydra client creation command
3. Save client ID and secret to `.env`
4. Update frontend configuration

**Deliverables:**
- Registered OAuth2 client in Hydra
- Client credentials stored in `.env`

**Client Creation Command:**
```bash
docker exec -it hydra-container hydra create client \
  --endpoint http://localhost:4445 \
  --name "FastAPI Resource Server" \
  --grant-type authorization_code,refresh_token \
  --response-type code \
  --scope openid,offline,data:read,data:write,data:update,data:delete \
  --redirect-uri http://localhost:8080/callback \
  --token-endpoint-auth-method client_secret_post
```

**Output:**
```
CLIENT ID       your-generated-client-id
CLIENT SECRET   your-generated-client-secret
```

**Testing:**
```bash
# Verify client exists
docker exec hydra-container hydra get client \
  --endpoint http://localhost:4445 \
  your-generated-client-id
```

---

### 📋 Phase 12: Keto Permissions Setup

**Goal:** Load user roles and permissions into Keto

**Tasks:**
1. Verify `ory/keto/scopes_roles_permissions.json` is up to date
2. Ensure load-permissions script is configured
3. Run permission loading script
4. Verify permissions in Keto

**Deliverables:**
- Updated permissions JSON
- Loaded permissions in Keto
- Verified user-role-permission relationships

**Permissions Structure:**
```json
{
  "namespace": "fastapi-resource-server",
  "roles": {
    "data:admin": {
      "permissions": ["data:read", "data:write", "data:update", "data:delete"]
    },
    "data:operator": {
      "permissions": ["data:read", "data:write", "data:update"]
    },
    "data:user": {
      "permissions": ["data:read"]
    }
  },
  "users": {
    "github_username_1": {
      "roles": ["data:admin"]
    },
    "github_username_2": {
      "roles": ["data:user"]
    }
  }
}
```

**Testing:**
```bash
# Verify permissions loaded
docker exec keto-container keto relation-tuples get-all \
  --read-remote http://localhost:4466 \
  --insecure

# Check specific user permissions
curl "http://localhost:4466/relation-tuples?namespace=fastapi-resource-server&subject_id=username"
```

---

### 📋 Phase 13: Integration Testing

**Goal:** Test complete OAuth2 flow end-to-end

**Tasks:**
1. Start all services with docker-compose
2. Test complete login flow
3. Test token usage with protected endpoints
4. Test scope-based access control
5. Test enhancement features (refresh, introspect)
6. Test error scenarios

**Deliverables:**
- Working end-to-end OAuth2 flow
- Verified protected endpoints
- Verified Keto permission enforcement
- Test documentation

**Test Scenarios:**

#### Scenario 1: Complete Auth Flow
```bash
1. Open http://localhost:8080/
2. Click "Login with GitHub"
3. Authenticate with GitHub
4. Verify redirect to /callback
5. Verify token displayed
6. Copy token
```

#### Scenario 2: Protected Endpoint Access
```bash
# Test with valid token
TOKEN="ory_at_your_token_here"

# Should succeed (user has data:read)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/users

# Should succeed (user has data:write)
curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"entity": "users", "name": "Test User", "email": "test@example.com"}'
```

#### Scenario 3: Scope Enforcement
```bash
# If user only has data:read, this should fail with 403
curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"entity": "users", "name": "Test", "email": "test@example.com"}'
```

#### Scenario 4: Token Refresh
```bash
# Get refresh token from initial login
REFRESH_TOKEN="ory_rt_your_refresh_token"

# Exchange for new access token
curl -X POST http://localhost:8080/auth/refresh \
  -d "grant_type=refresh_token&refresh_token=$REFRESH_TOKEN"
```

#### Scenario 5: Token Introspection
```bash
# Check token validity
curl -X POST http://localhost:8080/auth/introspect \
  -d "token=$TOKEN"
```

**Testing Checklist:**
- [ ] Login flow completes successfully
- [ ] Token displayed on callback page
- [ ] Token works with protected endpoints
- [ ] Scope enforcement works correctly
- [ ] Invalid token returns 401
- [ ] Missing token returns 401
- [ ] Insufficient scope returns 403
- [ ] Token refresh works
- [ ] Token introspection works
- [ ] GitHub OAuth errors handled
- [ ] Hydra errors handled

---

### 📋 Phase 14: Error Handling & Edge Cases

**Goal:** Handle errors gracefully

**Tasks:**
1. Add comprehensive error handling in auth routes
2. Add user-friendly error messages
3. Add proper HTTP status codes
4. Add logging for debugging
5. Handle edge cases

**Deliverables:**
- Comprehensive error handling
- User-friendly error messages
- Proper HTTP status codes
- Structured logging

**Error Scenarios to Handle:**

| Scenario | HTTP Status | User Message |
|----------|-------------|--------------|
| Missing login_challenge | 400 | "Missing login challenge parameter" |
| Missing consent_challenge | 400 | "Missing consent challenge parameter" |
| Invalid state parameter | 400 | "Invalid state - possible CSRF attack" |
| GitHub OAuth error | 400 | "GitHub authentication failed: {error}" |
| Token exchange failure | 400/401 | "Failed to exchange authorization code" |
| Invalid token | 401 | "Invalid or expired token" |
| Missing token | 401 | "Authorization header required" |
| Insufficient scope | 403 | "Insufficient permissions. Required: {scope}" |
| Hydra connection error | 503 | "Authentication service unavailable" |
| Keto connection error | 503 | "Permission service unavailable" |

**Logging Strategy:**
```python
logger.info(f"User {username} authenticated successfully")
logger.warning(f"Failed login attempt with invalid challenge: {challenge}")
logger.error(f"Hydra introspection failed: {error}")
```

**Testing:**
```bash
# Test various error scenarios
curl http://localhost:8080/auth/login  # Missing challenge
curl -H "Authorization: Bearer invalid" http://localhost:8080/users
curl http://localhost:8080/users  # Missing auth header
```

---

### 📋 Phase 15: Documentation & README

**Goal:** Document the complete system

**Tasks:**
1. Create comprehensive README for FastAPI-Resource-Server
2. Document architecture and design decisions
3. Write setup instructions
4. Document API endpoints
5. Provide usage examples
6. Create troubleshooting guide

**Deliverables:**
- Complete `README.md`
- API documentation
- Setup guide
- Usage examples
- Troubleshooting guide

**README Sections:**
1. **Overview** - What this project does
2. **Architecture** - System components and flow
3. **Features** - OAuth2, GitHub, Keto, etc.
4. **Prerequisites** - Docker, GitHub OAuth app, etc.
5. **Setup Instructions** - Step-by-step guide
6. **Getting a Token** - How to authenticate
7. **Using the API** - Examples with curl, httpie, Postman
8. **Available Endpoints** - API reference
9. **Scopes & Permissions** - What each scope allows
10. **Environment Variables** - Configuration reference
11. **Troubleshooting** - Common issues and solutions
12. **Development** - Running tests, contributing

**Example Usage:**
```bash
# Get a token
1. Open http://localhost:8080/
2. Click "Login with GitHub"
3. Copy the displayed token

# Use the token
export TOKEN="ory_at_your_token_here"

# List users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/users

# Create user
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8080/users \
  -d '{"entity": "users", "name": "John Doe", "email": "john@example.com"}'
```

---

### 📋 Phase 16: Optional Enhancements

**Goal:** Add nice-to-have features

**Optional Features:**

#### 16.1: Token Revocation
```python
@router.post("/auth/revoke")
async def revoke_token(request: Request):
    """Revoke an access or refresh token"""
```

#### 16.2: Logout Page
```html
<!-- static/logout.html -->
User-friendly logout page that revokes token
```

#### 16.3: Token Expiration Countdown
```javascript
// Add to callback.html
Display countdown timer for token expiration
```

#### 16.4: User Profile Page
```html
<!-- static/profile.html -->
Show user info and granted scopes
```

#### 16.5: CLI Tool
```python
# tools/get-token.py
Python CLI tool for easier token retrieval
```

#### 16.6: Postman Collection
```json
{
  "info": { "name": "FastAPI Resource Server" },
  "item": [...]
}
```

#### 16.7: Health Checks
```python
@router.get("/health/hydra")
async def check_hydra_health():
    """Check if Hydra is accessible"""

@router.get("/health/keto")
async def check_keto_health():
    """Check if Keto is accessible"""
```

#### 16.8: Metrics Endpoint
```python
@router.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics"""
```

**Deliverables:**
- Selected enhancement features
- Updated documentation
- Tests for new features

---

## Phase Dependency Chart

```
Phase 1: Setup & Dependencies
    ↓
    ├─→ Phase 2: Keto Integration
    ├─→ Phase 3: GitHub Provider
    └─→ Phase 4: OAuth2 Dependencies
         ↓
         └─→ Phase 5: Hydra Flow Handlers (needs 2, 3, 4)
              ↓
              └─→ Phase 6: Proxy Endpoints
                   ↓
                   └─→ Phase 7: HTML Pages
                        ↓
                        └─→ Phase 8: Protect Routes
                             ↓
                             └─→ Phase 9: Docker Compose
                                  ↓
                                  └─→ Phase 10: Environment Config
                                       ↓
                                       ├─→ Phase 11: Hydra Client
                                       └─→ Phase 12: Keto Permissions
                                            ↓
                                            └─→ Phase 13: Integration Testing
                                                 ↓
                                                 ├─→ Phase 14: Error Handling
                                                 ├─→ Phase 15: Documentation
                                                 └─→ Phase 16: Enhancements
```

---

## Recommended Implementation Order

### Sprint 1: Core Setup (Phases 1-4)
**Duration:** 2-3 hours  
**Focus:** Build the foundation

**Phases:**
1. Project Setup & Dependencies
2. Keto Integration
3. GitHub OAuth Provider
4. Token Validation & OAuth2 Dependencies

**Checkpoint:** All core auth modules are implemented and unit tested

---

### Sprint 2: OAuth2 Flow (Phases 5-7)
**Duration:** 3-4 hours  
**Focus:** Implement the complete OAuth2 authorization code flow

**Phases:**
5. Auth Routes - Hydra Flow Handlers
6. Auth Routes - Client Proxy Endpoints
7. Static File Serving & HTML Pages

**Checkpoint:** User can login via browser and get a token

---

### Sprint 3: Security & Integration (Phases 8-10)
**Duration:** 2-3 hours  
**Focus:** Protect routes and configure services

**Phases:**
8. Protect Existing Routes
9. Docker Compose & Ory Services
10. Environment Configuration & Secrets

**Checkpoint:** Protected endpoints work with valid tokens

---

### Sprint 4: Deployment (Phases 11-13)
**Duration:** 2-3 hours  
**Focus:** Set up Hydra/Keto and test end-to-end

**Phases:**
11. Hydra Client Registration
12. Keto Permissions Setup
13. Integration Testing

**Checkpoint:** Complete end-to-end flow works, all tests pass

---

### Sprint 5: Polish (Phases 14-16)
**Duration:** 2-3 hours  
**Focus:** Error handling, documentation, enhancements

**Phases:**
14. Error Handling & Edge Cases
15. Documentation & README
16. Optional Enhancements

**Checkpoint:** Production-ready application with complete documentation

---

## Testing Strategy

### Unit Tests
- Mock external services (Hydra, Keto, GitHub)
- Test individual functions and classes
- Use pytest with pytest-asyncio

### Integration Tests
- Test with real Ory services in Docker
- Test complete OAuth2 flow
- Test protected endpoints

### Manual Tests
- Browser-based login flow
- Token usage with curl/Postman
- Error scenarios

---

## Key Design Decisions

### 1. Opaque Tokens vs JWT
**Decision:** Use opaque tokens (Hydra default)  
**Reason:** Better security, instant revocation, dynamic permissions

### 2. Backend Proxy vs Direct Client Access
**Decision:** Proxy all OAuth2 endpoints through FastAPI  
**Reason:** Hide Hydra from clients, easier to migrate auth providers

### 3. One-Time Token Display
**Decision:** Show token once, no storage, clear on refresh  
**Reason:** Security - prevent token leakage, force re-authentication

### 4. Confidential Client with PKCE
**Decision:** Use both client_secret (backend) and PKCE (frontend)  
**Reason:** Defense in depth, supports both patterns

### 5. Keto for Dynamic Permissions
**Decision:** Check Keto at consent time for scopes  
**Reason:** Centralized permission management, dynamic updates

---

## Success Criteria

### Phase 1-4 Complete When:
- [ ] All dependencies installed
- [ ] Settings load from environment
- [ ] Auth modules pass unit tests
- [ ] No import errors

### Phase 5-7 Complete When:
- [ ] User can click login button
- [ ] GitHub auth completes
- [ ] Token displays on callback page
- [ ] No runtime errors in flow

### Phase 8-10 Complete When:
- [ ] Protected endpoints require token
- [ ] Invalid token returns 401
- [ ] Docker services start successfully
- [ ] Environment variables loaded

### Phase 11-13 Complete When:
- [ ] Hydra client registered
- [ ] Keto permissions loaded
- [ ] Complete flow works end-to-end
- [ ] All test scenarios pass

### Phase 14-16 Complete When:
- [ ] Errors handled gracefully
- [ ] Documentation complete
- [ ] README provides clear setup instructions
- [ ] Optional features implemented (if selected)

---

## Quick Start (After Implementation)

```bash
# 1. Clone and navigate
cd FastAPI-Resource-Server

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials

# 3. Start services
docker-compose -f ory/docker-compose.yml up -d

# 4. Create Hydra client
docker exec hydra hydra create client \
  --endpoint http://localhost:4445 \
  --name "FastAPI Resource Server" \
  --grant-type authorization_code,refresh_token \
  --response-type code \
  --scope openid,offline,data:read,data:write,data:update,data:delete \
  --redirect-uri http://localhost:8080/callback

# 5. Update .env with client ID/secret

# 6. Load Keto permissions
docker exec keto /scripts/load-permissions.sh

# 7. Get token
open http://localhost:8080/

# 8. Use token
export TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/users
```

---

## Support & Resources

### Documentation
- [Ory Hydra Docs](https://www.ory.sh/docs/hydra)
- [Ory Keto Docs](https://www.ory.sh/docs/keto)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [GitHub OAuth Docs](https://docs.github.com/en/developers/apps/building-oauth-apps)

### Troubleshooting
- Check Docker logs: `docker-compose logs -f`
- Verify Hydra: `curl http://localhost:4445/health/ready`
- Verify Keto: `curl http://localhost:4466/health/ready`
- Check environment: `python -c "from config.settings import Settings; print(Settings())"`

---

## Notes

- This implementation follows OAuth2 RFC 6749 (Authorization Code Grant)
- Uses PKCE (RFC 7636) for additional security
- Follows FastAPI best practices for dependency injection
- Implements separation of concerns (auth, business logic, data access)
- Ready for production with proper error handling and logging

---
