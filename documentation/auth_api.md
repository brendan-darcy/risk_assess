# CoreLogic API Authentication

Secure OAuth 2.0 authentication and authorization for CoreLogic API clients.

## Overview

CoreLogic APIs use the OAuth 2.0 protocol to enable applications to securely authenticate and request access tokens. The system supports multiple grant types and provides JWT-based access tokens for API authorization.

**Authentication Endpoint:** `https://api.corelogic.asia/access/as/token.oauth2`

## Key Features

- **OAuth 2.0 Protocol**: Industry standard authentication framework
- **JWT Access Tokens**: JSON Web Tokens with embedded expiry information
- **Multiple Grant Types**: Client credentials, authorization code, refresh token
- **Secure Transport**: HTTPS with TLSv1.2 minimum required
- **Token Caching**: Recommended for optimal performance

## Authentication Flow

### 4-Step Integration Process

1. **Retrieve Credentials**: Obtain client ID and client secret from CoreLogic
2. **Request Access Token**: Use credentials with OAuth Token Service
3. **Present Token**: Include access token in Authorization header for all API requests
4. **Refresh Token**: Refresh access token before expiry for uninterrupted service

## Supported Grant Types

| Grant Type | Description | Use Case |
|------------|-------------|----------|
| `client_credentials` | Service-to-service authentication | Server applications, batch processing |
| `authorization_code` | User authorization with redirect | Web applications requiring user consent |
| `refresh_token` | Token renewal without re-authentication | Maintaining long-term access |

## Token Request Examples

### Client Credentials Grant

**Standard Token Endpoint**
```bash
curl --location --request POST 'https://api.corelogic.asia/access/as/token.oauth2?grant_type=client_credentials' \
  --header 'Content-Length: 0' \
  --header 'Authorization: Basic <Base64 Encoded client_id:client_secret>'
```

**Legacy Token Endpoint (PSX APIs)**
```bash
curl --location --request POST 'https://api.corelogic.asia/access/oauth/token?grant_type=client_credentials' \
  --header 'Content-Length: 0' \
  --header 'Authorization: Basic <Base64 Encoded client_id:client_secret>'
```

### Authorization Code Grant

**Step 1: Authorization Request**
```bash
GET https://api.corelogic.asia/access/as/authorization.oauth2?
  response_type=code&
  client_id={client_id}&
  redirect_uri={redirect_uri}&
  scope={scope}&
  state={state}
```

**Step 2: Token Exchange**
```bash
curl --location --request POST 'https://api.corelogic.asia/access/as/token.oauth2' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --header 'Authorization: Basic <Base64 Encoded client_id:client_secret>' \
  --data-urlencode 'grant_type=authorization_code' \
  --data-urlencode 'code={authorization_code}' \
  --data-urlencode 'redirect_uri={redirect_uri}'
```

### Refresh Token Grant

```bash
curl --location --request POST 'https://api.corelogic.asia/access/as/token.oauth2' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --header 'Authorization: Basic <Base64 Encoded client_id:client_secret>' \
  --data-urlencode 'grant_type=refresh_token' \
  --data-urlencode 'refresh_token={refresh_token}'
```

## Response Schemas

### Successful Token Response
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEyMyJ9.eyJzdWIiOiJjbGllbnRfaWQiLCJpc3MiOiJodHRwczovL2FwaS5jb3JlbG9naWMuYXNpYSIsImF1ZCI6WyJhcGktc2VydmljZSJdLCJleHAiOjE2OTM0NDEyMDAsImlhdCI6MTY5MzQzNzYwMCwic2NvcGUiOlsicmVhZCIsIndyaXRlIl0sImNsaWVudF9pZCI6InlvdXJfY2xpZW50X2lkIn0.signature_data_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write",
  "refresh_token": "def502002f3e5c8c7b1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

### Authorization Code Response (Step 1)
```json
{
  "code": "SplxlOBeZQQYbYS6WxSbIA",
  "state": "xyz"
}
```

### Error Response
```json
{
  "error": "invalid_client",
  "error_description": "Client authentication failed",
  "error_uri": "https://docs.corelogic.asia/errors#invalid_client"
}
```

## JWT Token Structure

Access tokens are JSON Web Tokens containing:

### Header
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "123"
}
```

### Payload
```json
{
  "sub": "client_id",
  "iss": "https://api.corelogic.asia",
  "aud": ["api-service"],
  "exp": 1693441200,
  "iat": 1693437600,
  "scope": ["read", "write"],
  "client_id": "your_client_id"
}
```

### Key Claims
- **`sub`**: Subject (client identifier)
- **`iss`**: Issuer (CoreLogic authentication server)
- **`aud`**: Audience (target API services)
- **`exp`**: Expiration time (Unix epoch timestamp)
- **`iat`**: Issued at time
- **`scope`**: Granted permissions
- **`client_id`**: OAuth2 client identifier

## Making Authenticated API Calls

### Authorization Header Format
```
Authorization: Bearer {access_token}
```

### Example API Request
```bash
curl -X 'GET' \
  'https://api-sbox.corelogic.asia/property/au/v2/suggest.json?q=2%20Albert%20Avenue%20Broadbeach%20QLD%204218' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGxxxxxxxxxxxxxxxxxxxxxxxWQ'
```

### API Response with System Info
```json
{
  "suggestions": [
    {
      "councilAreaId": 284,
      "countryId": 113,
      "isActiveProperty": true,
      "isBodyCorporate": false,
      "isUnit": false,
      "localityId": 3723,
      "postcodeId": 300303,
      "propertyId": 47872329,
      "stateId": 3,
      "streetId": 38135,
      "suggestion": "2 Albert Avenue Broadbeach QLD 4218",
      "suggestionType": "address"
    }
  ],
  "systemInfo": {
    "instanceName": "139:8080",
    "requestDate": "2024-06-26T01:50:17.949Z"
  }
}
```

## Token Management

### Token Expiry Handling
- Decode JWT to extract `exp` claim for expiry time
- Implement token refresh before expiry
- Handle `401 Unauthorized` responses gracefully
- Cache tokens securely to avoid unnecessary requests

### Security Best Practices
1. **Secure Storage**: Store credentials and tokens securely
2. **HTTPS Only**: All requests must use HTTPS with TLSv1.2+
3. **Token Rotation**: Regularly refresh tokens
4. **Scope Limitation**: Request only necessary scopes
5. **Error Handling**: Implement proper error handling for auth failures

### Sample Token Management Code
```python
import jwt
import time
import base64
import requests
from datetime import datetime

class CoreLogicAuth:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> str:
        if self.access_token and self.token_expires_at > time.time() + 300:
            return self.access_token
        
        return self._refresh_token()
    
    def _refresh_token(self) -> str:
        auth_string = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_string}',
            'Content-Length': '0'
        }
        
        response = requests.post(
            'https://api.corelogic.asia/access/as/token.oauth2?grant_type=client_credentials',
            headers=headers
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Decode JWT to get actual expiry
            decoded = jwt.decode(self.access_token, verify=False)
            self.token_expires_at = decoded['exp']
            
            return self.access_token
        else:
            raise Exception(f"Token request failed: {response.status_code}")
```

## Error Codes

| Error | Description | Resolution |
|-------|-------------|------------|
| `invalid_client` | Client authentication failed | Verify client credentials |
| `invalid_grant` | Grant type not supported | Check grant_type parameter |
| `invalid_scope` | Requested scope invalid | Request valid scopes only |
| `unsupported_grant_type` | Grant type not supported | Use supported grant types |
| `access_denied` | Authorization denied | Check permissions and retry |

## Environment-Specific Endpoints

| Environment | Token Endpoint | API Base URL |
|-------------|----------------|--------------|
| **Sandbox** | `https://api.corelogic.asia/access/as/token.oauth2` | `https://api-sbox.corelogic.asia` |
| **Production** | `https://api.corelogic.asia/access/as/token.oauth2` | `https://api.corelogic.asia` |
| **Legacy (PSX)** | `https://api.corelogic.asia/access/oauth/token` | `https://api.corelogic.asia` |

## Rate Limiting

- Token requests are subject to rate limiting
- Implement exponential backoff for failed requests
- Cache tokens to minimize authentication requests
- Monitor `Retry-After` headers in rate limit responses

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Token expired or invalid
2. **403 Forbidden**: Insufficient permissions
3. **400 Bad Request**: Invalid request parameters
4. **500 Server Error**: Temporary service issue

### Debug Steps
1. Verify credentials are correct
2. Check token expiry using JWT decoder
3. Ensure HTTPS is used for all requests
4. Validate Authorization header format
5. Check API endpoint URLs

---

*© RP Data Pty Limited trading as Cotality (ABN 67 087 759 171) and CoreLogic NZ Limited trading as Cotality (NZCN 1129102) 2025. All rights reserved.*