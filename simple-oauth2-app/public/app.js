// Configuration - clientId will be loaded from server
const config = {
    clientId: null, // Loaded from /config.js
    redirectUri: 'http://localhost:3000/callback',
    authorizationEndpoint: 'http://localhost:4444/oauth2/auth',
    tokenEndpoint: '/token', // Proxied through our server
    userinfoEndpoint: '/userinfo', // Proxied through our server
    scope: 'openid offline records:read records:write records:delete posts:read posts:write admin users:read'
};

// Generate random string for state and PKCE
function generateRandomString(length = 43) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let result = '';
    const randomValues = new Uint8Array(length);
    crypto.getRandomValues(randomValues);
    for (let i = 0; i < length; i++) {
        result += charset[randomValues[i] % charset.length];
    }
    return result;
}

// Generate PKCE code challenge
async function generateCodeChallenge(codeVerifier) {
    const encoder = new TextEncoder();
    const data = encoder.encode(codeVerifier);
    const hash = await crypto.subtle.digest('SHA-256', data);
    const base64 = btoa(String.fromCharCode(...new Uint8Array(hash)));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// Start login flow
async function login() {
    // Load client ID from server if not already loaded
    if (!config.clientId) {
        if (window.OAUTH2_CONFIG && window.OAUTH2_CONFIG.clientId) {
            config.clientId = window.OAUTH2_CONFIG.clientId;
        } else {
            alert('OAuth2 client configuration not loaded. Please refresh the page.');
            return;
        }
    }

    const state = generateRandomString();
    const codeVerifier = generateRandomString();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Store for later use
    sessionStorage.setItem('oauth_state', state);
    sessionStorage.setItem('code_verifier', codeVerifier);

    // Build authorization URL
    const params = new URLSearchParams({
        client_id: config.clientId,
        response_type: 'code',
        redirect_uri: config.redirectUri,
        scope: config.scope,
        state: state,
        code_challenge: codeChallenge,
        code_challenge_method: 'S256'
    });

    window.location.href = `${config.authorizationEndpoint}?${params.toString()}`;
}

// Handle OAuth callback
async function handleCallback() {
    // Load client ID from server if not already loaded
    if (!config.clientId) {
        if (window.OAUTH2_CONFIG && window.OAUTH2_CONFIG.clientId) {
            config.clientId = window.OAUTH2_CONFIG.clientId;
        } else {
            alert('OAuth2 client configuration not loaded. Please refresh the page.');
            window.location.href = '/';
            return;
        }
    }

    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');

    if (error) {
        alert(`Authentication error: ${error}`);
        window.location.href = '/';
        return;
    }

    if (!code) {
        return; // Not a callback
    }

    const savedState = sessionStorage.getItem('oauth_state');
    if (state !== savedState) {
        alert('Invalid state parameter');
        window.location.href = '/';
        return;
    }

    const codeVerifier = sessionStorage.getItem('code_verifier');

    try {
        // Exchange code for tokens
        const tokenResponse = await fetch(config.tokenEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: config.redirectUri,
                client_id: config.clientId,
                code_verifier: codeVerifier
            })
        });

        if (!tokenResponse.ok) {
            const errorData = await tokenResponse.text();
            console.error('Token exchange failed:', errorData);
            throw new Error(`Token exchange failed: ${tokenResponse.status} - ${errorData}`);
        }

        const tokens = await tokenResponse.json();
        
        // Store tokens and scope
        sessionStorage.setItem('access_token', tokens.access_token);
        if (tokens.refresh_token) {
            sessionStorage.setItem('refresh_token', tokens.refresh_token);
        }
        if (tokens.scope) {
            sessionStorage.setItem('granted_scope', tokens.scope);
        }

        // Get user info
        const userinfoResponse = await fetch(config.userinfoEndpoint, {
            headers: {
                'Authorization': `Bearer ${tokens.access_token}`
            }
        });

        if (userinfoResponse.ok) {
            const userinfo = await userinfoResponse.json();
            sessionStorage.setItem('userinfo', JSON.stringify(userinfo));
        }

        // Clean up
        sessionStorage.removeItem('oauth_state');
        sessionStorage.removeItem('code_verifier');

        // Redirect to home
        window.location.href = '/';
    } catch (error) {
        console.error('Authentication error:', error);
        alert('Authentication failed');
        window.location.href = '/';
    }
}

// Display user info
function displayUserInfo() {
    const userinfo = sessionStorage.getItem('userinfo');
    const grantedScope = sessionStorage.getItem('granted_scope');
    
    if (userinfo) {
        const user = JSON.parse(userinfo);
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('userInfo').classList.add('show');
        
        let html = '';
        
        // Avatar
        if (user.avatar_url) {
            html += `<div class="info-item" style="text-align: center;">
                <img src="${user.avatar_url}" alt="Avatar" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 15px;">
            </div>`;
        }
        
        // Basic info
        if (user.name) html += `<div class="info-item"><strong>Name:</strong> ${user.name}</div>`;
        if (user.username) html += `<div class="info-item"><strong>Username:</strong> @${user.username}</div>`;
        if (user.email) html += `<div class="info-item"><strong>Email:</strong> ${user.email}</div>`;
        
        // Additional info
        if (user.bio) html += `<div class="info-item"><strong>Bio:</strong> ${user.bio}</div>`;
        if (user.company) html += `<div class="info-item"><strong>Company:</strong> ${user.company}</div>`;
        if (user.location) html += `<div class="info-item"><strong>Location:</strong> ${user.location}</div>`;
        if (user.blog) html += `<div class="info-item"><strong>Website:</strong> <a href="${user.blog}" target="_blank">${user.blog}</a></div>`;
        
        // GitHub stats
        if (user.public_repos !== undefined) html += `<div class="info-item"><strong>Public Repos:</strong> ${user.public_repos}</div>`;
        if (user.followers !== undefined) html += `<div class="info-item"><strong>Followers:</strong> ${user.followers}</div>`;
        if (user.following !== undefined) html += `<div class="info-item"><strong>Following:</strong> ${user.following}</div>`;
        
        // Account creation date
        if (user.created_at) {
            const date = new Date(user.created_at);
            html += `<div class="info-item"><strong>Member Since:</strong> ${date.toLocaleDateString()}</div>`;
        }
        
        if (user.sub) html += `<div class="info-item" style="font-size: 0.9em; color: #666;"><strong>User ID:</strong> ${user.sub}</div>`;
        
        // Granted scopes/permissions
        if (grantedScope) {
            const scopes = grantedScope.split(' ');
            const scopeBadges = scopes.map(scope => {
                const isCustom = !['openid', 'offline'].includes(scope);
                const color = isCustom ? '#28a745' : '#007bff';
                return `<span style="display: inline-block; background: ${color}; color: white; padding: 4px 10px; border-radius: 12px; margin: 3px; font-size: 0.85em;">${scope}</span>`;
            }).join('');
            html += `<div class="info-item" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                <strong>🎯 Granted Permissions:</strong>
                <div style="margin-top: 8px;">${scopeBadges}</div>
            </div>`;
        }
        
        document.getElementById('userDetails').innerHTML = html;
    }
}

// Logout
function logout() {
    sessionStorage.clear();
    window.location.href = '/';
}

// Initialize on page load
if (window.location.pathname === '/callback') {
    handleCallback();
} else {
    displayUserInfo();
}
