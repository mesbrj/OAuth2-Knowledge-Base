# JavaScript-Knowledge-Base

A collection of JavaScript examples and implementations.

## [(1) OAuth2 Authentication Application](/simple-oauth2-app/README.md)

OAuth2 Authorization Code flow implementation with Ory IAM.

- **Ory Hydra:** OAuth2 Authorization Code Flow with PKCE
    - GitHub as Identity Provider
- **Ory Keto:** Role-Based Access Control (RBAC)
    - Integrating in `consent` step of OAuth2 flow adding additional scopes to the access token
- No Ory SDK used, only HTTP API calls
    - *Educational purposes*

|App Index Login|Github Login|Github Permission Authorization|
|:-:|:-:|:-:|
|![](/simple-oauth2-app/docs/imgs/Index_login.png)|![](/simple-oauth2-app/docs/imgs/Github-login.png)|![](/simple-oauth2-app/docs/imgs/github-authorize.png)|![](/simple-oauth2-app/docs/imgs/loged-user-info.png)|

|mesbrj user info and grants|Soro-Kan user info and grants|
|:-:|:-:|
|![](/simple-oauth2-app/docs/imgs/loged-user-info.png)|![](/simple-oauth2-app/docs/imgs/loged-user2-info.png)|