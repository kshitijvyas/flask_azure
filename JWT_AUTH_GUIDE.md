# JWT Authentication - Testing Guide

## Overview
This project now includes JWT-based authentication using Flask-JWT-Extended. All sensitive endpoints require a valid access token.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to your `.env` file:
```properties
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

Or generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API Endpoints

### 1. Register a New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (201):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-11-13T10:00:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. Login (Get Tokens)
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

Or login with email:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200):
```json
{
  "message": "Login successful",
  "user": {...},
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 3. Get Current User Info
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response** (200):
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "avatar_url": null,
    "created_at": "2025-11-13T10:00:00"
  }
}
```

---

### 4. Refresh Access Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 5. Change Password
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "SecurePassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Response** (200):
```json
{
  "message": "Password changed successfully"
}
```

---

## Protected Endpoints

The following existing endpoints now require authentication:

### Update User Profile
```http
PUT /api/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "new_username"
}
```

**Note**: Users can only update their own profile (user_id must match token identity).

---

### Delete User Account
```http
DELETE /api/users/{user_id}
Authorization: Bearer <access_token>
```

**Note**: Users can only delete their own account.

---

### Upload Avatar
```http
POST /api/users/{user_id}/upload-avatar
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image_file>
```

**Note**: Users can only upload their own avatar.

---

## Public Endpoints (No Auth Required)

- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create user (deprecated - use `/api/auth/register`)

---

## Testing with Postman

### Step 1: Register
1. Create a POST request to `http://localhost:5000/api/auth/register`
2. Set body to JSON:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123"
   }
   ```
3. Send request
4. Copy the `access_token` from response

### Step 2: Access Protected Endpoint
1. Create a PUT request to `http://localhost:5000/api/users/1`
2. Go to **Authorization** tab
3. Select **Type**: Bearer Token
4. Paste the `access_token`
5. Set body to JSON:
   ```json
   {
     "username": "updated_username"
   }
   ```
6. Send request

### Step 3: Refresh Token
1. Create a POST request to `http://localhost:5000/api/auth/refresh`
2. Use **Bearer Token** with the `refresh_token` (not access_token)
3. Send request
4. Get new `access_token`

---

## Testing with PowerShell

### Register User
```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/auth/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Login
```powershell
$body = @{
    username = "testuser"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

$data = $response.Content | ConvertFrom-Json
$token = $data.access_token
```

### Access Protected Endpoint
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$body = @{
    username = "updated_name"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/users/1" `
    -Method PUT `
    -Headers $headers `
    -Body $body `
    -ContentType "application/json"
```

---

## Token Configuration

Default token lifetimes (configured in `app/config.py`):
- **Access Token**: 1 hour (3600 seconds)
- **Refresh Token**: 30 days (2592000 seconds)

To change:
```python
# app/config.py
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
```

---

## Error Responses

### 401 Unauthorized - Missing Token
```json
{
  "error": "Authorization required",
  "message": "Request does not contain an access token"
}
```

### 401 Unauthorized - Expired Token
```json
{
  "error": "Token has expired",
  "message": "Please login again"
}
```

### 401 Unauthorized - Invalid Token
```json
{
  "error": "Invalid token",
  "message": "Token verification failed"
}
```

### 403 Forbidden - Unauthorized Action
```json
{
  "error": "Unauthorized: You can only update your own profile"
}
```

---

## Security Best Practices

1. **HTTPS Only in Production**: Always use HTTPS to prevent token interception
2. **Secure Token Storage**:
   - Web apps: Use httpOnly cookies for refresh tokens
   - Mobile apps: Use secure storage (Keychain/Keystore)
   - SPAs: Store in memory or sessionStorage (not localStorage for refresh tokens)
3. **Short-lived Access Tokens**: Keep access tokens short (15-60 minutes)
4. **Refresh Token Rotation**: Implement refresh token rotation for extra security
5. **Token Revocation**: Use Redis/database to maintain a blacklist for logout
6. **Strong Passwords**: Enforce password complexity rules
7. **Rate Limiting**: Add rate limiting to prevent brute force attacks

---

## Next Steps: Role-Based Access Control (RBAC)

Coming next:
- Add `role` column to User model (admin, user)
- Create `@roles_required(['admin'])` decorator
- Protect admin-only endpoints (delete any user, view all salaries, etc.)

---

## Troubleshooting

### Issue: "Import flask_jwt_extended could not be resolved"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Token has expired"
**Solution**: Use the refresh token to get a new access token at `/api/auth/refresh`

### Issue: "Invalid token"
**Solution**: Make sure you're using the correct token type (access vs refresh) for the endpoint

### Issue: Password not being hashed
**Solution**: The User model now has `set_password()` and `check_password()` methods. Use these instead of directly setting `password_hash`.

---

## Development vs Production

### Development (.env)
```properties
FLASK_ENV=development
JWT_SECRET_KEY=dev-jwt-secret-not-secure
```

### Production (Azure App Service)
1. Generate secure key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Add to Azure Key Vault as `JWT-SECRET-KEY` secret
3. Or add to App Service environment variables as `JWT_SECRET_KEY`

---

## Summary

✅ **Implemented**:
- User registration with password hashing
- Login with JWT token generation
- Token refresh mechanism
- Protected routes with `@jwt_required()`
- User-specific authorization (users can only modify their own data)
- Password change functionality
- Comprehensive error handling

🔜 **Coming Next**:
- Role-based access control (admin/user roles)
- Token blacklist for logout
- Rate limiting for auth endpoints
- OAuth2 integration with Azure AD (optional)
