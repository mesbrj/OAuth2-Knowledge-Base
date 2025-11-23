require('dotenv').config();

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;
const HYDRA_ADMIN_URL = process.env.HYDRA_ADMIN_URL || 'http://localhost:4445';
const KETO_READ_URL = process.env.KETO_READ_URL || 'http://localhost:4466';
const KETO_WRITE_URL = process.env.KETO_WRITE_URL || 'http://localhost:4467';
const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
const OAUTH2_CLIENT_ID = process.env.OAUTH2_CLIENT_ID;
const KETO_NAMESPACE = 'simple-oauth2-app';

if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
    console.error('❌ Error: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set in .env file or environment variables');
    process.exit(1);
}

if (!OAUTH2_CLIENT_ID) {
    console.error('❌ Error: OAUTH2_CLIENT_ID must be set in .env file or environment variables');
    console.error('   Run the Hydra client creation command first (see README.md)');
    process.exit(1);
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// Config endpoint - serve OAuth2 client configuration
app.get('/config.js', (req, res) => {
    res.type('application/javascript');
    res.send(`window.OAUTH2_CONFIG = { clientId: '${OAUTH2_CLIENT_ID}' };`);
});

// Callback route - serve callback.html
app.get('/callback', (req, res) => {
    res.sendFile(__dirname + '/public/callback.html');
});

// Token exchange proxy endpoint
app.post('/token', async (req, res) => {
    try {
        const tokenResponse = await fetch('http://hydra:4444/oauth2/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(req.body).toString()
        });

        const data = await tokenResponse.json();
        
        if (!tokenResponse.ok) {
            return res.status(tokenResponse.status).json(data);
        }

        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Token exchange failed' });
    }
});

// Userinfo proxy endpoint
app.get('/userinfo', async (req, res) => {
    try {
        const authorization = req.headers.authorization;
        if (!authorization) {
            return res.status(401).json({ error: 'Missing authorization header' });
        }

        const userinfoResponse = await fetch('http://hydra:4444/userinfo', {
            headers: {
                'Authorization': authorization
            }
        });

        const data = await userinfoResponse.json();
        
        if (!userinfoResponse.ok) {
            return res.status(userinfoResponse.status).json(data);
        }

        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Userinfo request failed' });
    }
});

// Login endpoint - handle Hydra login challenge
app.get('/login', async (req, res) => {
    const loginChallenge = req.query.login_challenge;
    
    if (!loginChallenge) {
        return res.status(400).send('Missing login_challenge');
    }

    try {
        // Get login request info
        const loginReq = await fetch(`${HYDRA_ADMIN_URL}/admin/oauth2/auth/requests/login?login_challenge=${loginChallenge}`);
        const loginInfo = await loginReq.json();

        // For this example, we'll redirect to GitHub OAuth
        // In production, you'd have a proper login form
        const githubRedirectUri = 'http://localhost:3000/github-callback';
        const state = loginChallenge; // Pass challenge as state

        const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(githubRedirectUri)}&state=${state}&scope=read:user user:email`;
        
        res.redirect(githubAuthUrl);
    } catch (error) {
        res.status(500).send('Login failed');
    }
});

// GitHub callback
app.get('/github-callback', async (req, res) => {
    const code = req.query.code;
    const loginChallenge = req.query.state;

    if (!code || !loginChallenge) {
        return res.status(400).send('Missing code or state');
    }

    try {
        // Exchange GitHub code for access token
        const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                client_id: GITHUB_CLIENT_ID,
                client_secret: GITHUB_CLIENT_SECRET,
                code: code,
                redirect_uri: 'http://localhost:3000/github-callback'
            })
        });

        const tokenData = await tokenResponse.json();
        const accessToken = tokenData.access_token;

        // Get GitHub user info
        const userResponse = await fetch('https://api.github.com/user', {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
            }
        });

        const userData = await userResponse.json();

        // Accept the login challenge
        const acceptResponse = await fetch(`${HYDRA_ADMIN_URL}/admin/oauth2/auth/requests/login/accept?login_challenge=${loginChallenge}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: userData.id.toString(),
                remember: true,
                remember_for: 3600,
                context: {
                    username: userData.login,
                    email: userData.email,
                    name: userData.name,
                    avatar_url: userData.avatar_url,
                    bio: userData.bio,
                    company: userData.company,
                    location: userData.location,
                    blog: userData.blog,
                    public_repos: userData.public_repos,
                    followers: userData.followers,
                    following: userData.following,
                    created_at: userData.created_at
                }
            })
        });

        const acceptData = await acceptResponse.json();
        res.redirect(acceptData.redirect_to);
    } catch (error) {
        res.status(500).send('Authentication failed');
    }
});

// Helper function: Get user's scopes from Keto
async function getUserScopesFromKeto(username) {
    try {
        const params = new URLSearchParams({
            namespace: KETO_NAMESPACE,
            subject_id: username
        });
        
        const response = await fetch(`${KETO_READ_URL}/relation-tuples?${params}`);
        const data = await response.json();
        
        if (!data.relation_tuples) {
            return [];
        }
        
        // Extract permission objects (scopes)
        const scopes = data.relation_tuples
            .filter(tuple => tuple.relation === 'member') // User's roles
            .map(tuple => tuple.object);
        
        // Now get permissions for those roles
        const allPermissions = [];
        for (const role of scopes) {
            const roleParams = new URLSearchParams({
                namespace: KETO_NAMESPACE,
                'subject_set.namespace': KETO_NAMESPACE,
                'subject_set.object': role,
                'subject_set.relation': 'member'
            });
            
            const permResponse = await fetch(`${KETO_READ_URL}/relation-tuples?${roleParams}`);
            const permData = await permResponse.json();
            
            if (permData.relation_tuples) {
                permData.relation_tuples.forEach(tuple => {
                    if (tuple.relation === 'granted') {
                        allPermissions.push(tuple.object);
                    }
                });
            }
        }
        
        return [...new Set(allPermissions)]; // Remove duplicates
    } catch (error) {
        return [];
    }
}

// Consent endpoint - with Keto integration
app.get('/consent', async (req, res) => {
    const consentChallenge = req.query.consent_challenge;

    if (!consentChallenge) {
        return res.status(400).send('Missing consent_challenge');
    }

    try {
        // Get consent request info
        const consentReq = await fetch(`${HYDRA_ADMIN_URL}/admin/oauth2/auth/requests/consent?consent_challenge=${consentChallenge}`);
        const consentInfo = await consentReq.json();

        const username = consentInfo.context.username;
        const requestedScopes = consentInfo.requested_scope;
        
        // Get user's permissions from Keto
        const userPermissions = await getUserScopesFromKeto(username);
        
        // Grant scopes that user has permission for
        // Always grant openid and offline (OAuth2 basics)
        const grantedScopes = requestedScopes.filter(scope => {
            if (scope === 'openid' || scope === 'offline') return true;
            return userPermissions.includes(scope);
        });

        // Accept consent with filtered scopes
        const acceptResponse = await fetch(`${HYDRA_ADMIN_URL}/admin/oauth2/auth/requests/consent/accept?consent_challenge=${consentChallenge}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                grant_scope: grantedScopes,
                grant_access_token_audience: consentInfo.requested_access_token_audience,
                remember: true,
                remember_for: 3600,
                session: {
                    id_token: {
                        ...consentInfo.context,
                        scopes: grantedScopes
                    }
                }
            })
        });

        const acceptData = await acceptResponse.json();
        res.redirect(acceptData.redirect_to);
    } catch (error) {
        res.status(500).send('Consent failed');
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
