# Design Document: Authentication & User Management

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md

## Overview

This document defines the authentication system and user management architecture for the SaaS platform, including Google OAuth integration, multi-tenant organization model, and role-based access control.

## Requirements

### Functional Requirements

1. **Authentication**
   - Users must sign in with Google OAuth
   - Support for Google Workspace (optional)
   - JWT-based session management
   - Refresh token support

2. **User Management**
   - User profile management
   - Email verification
   - Password reset (if adding password auth later)
   - Account deletion (GDPR compliance)

3. **Organization Management**
   - Auto-create personal organization on signup
   - Support multiple organizations per user (future)
   - Organization member management
   - Role-based permissions

4. **Multi-tenancy**
   - Complete data isolation per organization
   - Organization-scoped sessions
   - Organization-scoped artifacts

## Google OAuth Integration

### OAuth Flow

```
┌──────────┐         ┌──────────┐         ┌─────────────┐
│ Frontend │ ──────> │  Google  │ ──────> │   Backend   │
│   (User) │ <────── │  OAuth   │ <────── │   (API)     │
└──────────┘         └──────────┘         └─────────────┘
     │                                         │
     │                                         │
     └────────── JWT Token ───────────────────┘
```

### Implementation Details

#### Frontend (OAuth Initiation)

```typescript
// frontend/auth/googleAuth.ts
export const initiateGoogleLogin = () => {
  const state = generateStateToken();
  localStorage.setItem('oauth_state', state);
  
  const params = new URLSearchParams({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    redirect_uri: `${window.location.origin}/auth/callback`,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'offline',
    prompt: 'consent',
    state: state
  });
  
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
};
```

#### Backend (OAuth Callback Handler)

```python
# backend/routes/auth.py
@router.post("/auth/google/callback")
async def google_callback(request: GoogleCallbackRequest):
    """
    Handle Google OAuth callback
    
    Flow:
    1. Verify state token (CSRF protection)
    2. Exchange code for tokens
    3. Verify ID token
    4. Get or create user
    5. Ensure organization exists
    6. Generate JWT
    7. Return to frontend
    """
    
    # 1. Verify state
    if request.state != get_stored_state(request.state):
        raise HTTPException(400, "Invalid state token")
    
    # 2. Exchange code for tokens
    tokens = await exchange_code_for_tokens(request.code)
    
    # 3. Verify ID token
    user_info = await verify_google_id_token(tokens["id_token"])
    
    # 4. Get or create user
    user = await get_or_create_user(user_info)
    
    # 5. Ensure organization exists
    org = await ensure_user_organization(user)
    
    # 6. Generate JWT
    jwt_token = create_jwt_token(user, org)
    
    # 7. Store refresh token (if provided)
    if "refresh_token" in tokens:
        await store_refresh_token(user.user_id, tokens["refresh_token"])
    
    return {
        "access_token": jwt_token,
        "refresh_token": tokens.get("refresh_token"),
        "user": serialize_user(user),
        "organization": serialize_organization(org)
    }
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    picture_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    auth_provider VARCHAR(50) DEFAULT 'google',
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb,
    current_organization_id UUID REFERENCES organizations(organization_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
```

### Organizations Table

```sql
CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'personal', 'team', 'enterprise'
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMP,
    subscription_ends_at TIMESTAMP,
    max_users INTEGER DEFAULT 1,
    max_sessions_per_month INTEGER,
    max_artifacts_storage_gb DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_organizations_subscription_status ON organizations(subscription_status);
```

### Organization Members Table

```sql
CREATE TABLE organization_members (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'owner', 'admin', 'member', 'viewer'
    invited_by UUID REFERENCES users(user_id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);

CREATE INDEX idx_org_members_org_id ON organization_members(organization_id);
CREATE INDEX idx_org_members_user_id ON organization_members(user_id);
```

## JWT Token Structure

### Access Token Payload

```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "name": "User Name",
  "org_id": "organization_id_uuid",
  "org_name": "Organization Name",
  "role": "owner",
  "tier": "pro",
  "iat": 1704067200,
  "exp": 1704153600,
  "type": "access"
}
```

### Token Expiration
- **Access Token**: 24 hours
- **Refresh Token**: 30 days

### Token Refresh Flow

```python
@router.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    
    # 1. Verify refresh token
    stored_token = db.refresh_tokens.get(request.refresh_token)
    if not stored_token or stored_token.expires_at < datetime.now():
        raise HTTPException(401, "Invalid refresh token")
    
    # 2. Get user and organization
    user = db.users.get(stored_token.user_id)
    org = db.organizations.get(stored_token.organization_id)
    
    # 3. Generate new access token
    new_access_token = create_jwt_token(user, org)
    
    return {
        "access_token": new_access_token,
        "refresh_token": stored_token.token  # Keep same refresh token
    }
```

## Organization Auto-Creation

### Flow on First Signup

```python
async def ensure_user_organization(user: User) -> Organization:
    """Ensure user has at least one organization"""
    
    # Check if user already belongs to an organization
    existing_memberships = db.organization_members.get_by_user(user.user_id)
    
    if existing_memberships:
        return db.organizations.get(existing_memberships[0].organization_id)
    
    # Create personal organization
    org = db.organizations.create({
        "name": f"{user.name}'s Workspace" if user.name else f"{user.email}'s Workspace",
        "type": "personal",
        "subscription_tier": "free",
        "subscription_status": "active",
        "created_by": user.user_id,
        "max_users": 1,
        "max_sessions_per_month": 50,
        "max_artifacts_storage_gb": 0.1
    })
    
    # Add user as owner
    db.organization_members.create({
        "organization_id": org.organization_id,
        "user_id": user.user_id,
        "role": "owner"
    })
    
    return org
```

## Role-Based Access Control (RBAC)

### Roles

| Role | Permissions |
|------|-------------|
| **Owner** | Full access: manage org, billing, users, delete org |
| **Admin** | Manage users, sessions, conversations (no billing) |
| **Member** | Create sessions, generate artifacts, view org data |
| **Viewer** | Read-only: view sessions, conversations, artifacts |

### Permission Checks

```python
# backend/middleware/rbac.py
def require_role(required_role: str):
    """Decorator to check user role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('user')  # From Depends(get_current_user)
            
            # Get user's role in organization
            org_id = user.get("org_id")
            membership = db.organization_members.get_by_user_and_org(
                user["sub"], org_id
            )
            
            if not membership:
                raise HTTPException(403, "Not a member of this organization")
            
            # Check role hierarchy
            role_hierarchy = {"owner": 4, "admin": 3, "member": 2, "viewer": 1}
            user_role_level = role_hierarchy.get(membership.role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            if user_role_level < required_level:
                raise HTTPException(403, f"Requires {required_role} role")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.delete("/organizations/{org_id}")
@require_role("owner")
async def delete_organization(org_id: str, user: dict = Depends(get_current_user)):
    """Only owners can delete organizations"""
    pass
```

## User Profile Management

### API Endpoints

```python
@router.get("/api/users/me")
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    user_obj = db.users.get(user["sub"])
    return serialize_user(user_obj)

@router.put("/api/users/me")
async def update_user_profile(
    profile: UserProfileUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user_obj = db.users.get(user["sub"])
    
    # Update allowed fields
    if profile.name:
        user_obj.name = profile.name
    if profile.preferences:
        user_obj.preferences = profile.preferences
    
    db.users.update(user["sub"], user_obj)
    return serialize_user(user_obj)
```

### Frontend Profile Page

```typescript
// frontend/pages/Settings/Profile.tsx
export const ProfileSettings: React.FC = () => {
  const [user, setUser] = useState(null);
  
  const handleUpdate = async (data: UserProfileUpdate) => {
    const response = await fetch('/api/users/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      setUser(await response.json());
      toast.success('Profile updated');
    }
  };
  
  return (
    <div>
      <h2>Profile Settings</h2>
      <ProfileForm user={user} onSubmit={handleUpdate} />
    </div>
  );
};
```

## Account Deletion (GDPR)

### Deletion Flow

```python
@router.delete("/api/users/me")
async def delete_account(user: dict = Depends(get_current_user)):
    """Delete user account and all associated data (GDPR)"""
    
    user_id = user["sub"]
    
    # 1. Export user data first (if requested)
    # await export_user_data(user_id)
    
    # 2. Delete user's organizations (if owner)
    orgs = db.organizations.get_by_owner(user_id)
    for org in orgs:
        await delete_organization(org.organization_id, user_id)
    
    # 3. Remove from organizations (as member)
    memberships = db.organization_members.get_by_user(user_id)
    for membership in memberships:
        db.organization_members.delete(membership.member_id)
    
    # 4. Delete user's sessions
    db.sessions.delete_by_user(user_id)
    
    # 5. Delete user's conversations
    db.conversations.delete_by_user(user_id)
    
    # 6. Delete artifacts (from S3)
    await delete_user_artifacts(user_id)
    
    # 7. Delete user record
    db.users.delete(user_id)
    
    # 8. Invalidate refresh tokens
    db.refresh_tokens.delete_by_user(user_id)
    
    return {"status": "deleted"}
```

## Security Considerations

### Token Storage
- **Frontend**: `localStorage` or `sessionStorage` (HTTPS only)
- **Backend**: Refresh tokens in database (encrypted)

### Token Validation
- Verify JWT signature
- Check expiration
- Validate organization still exists
- Verify user still active

### CSRF Protection
- State token in OAuth flow
- JWT tokens in Authorization header (not cookies)

### Rate Limiting
- Login attempts: 5 per 15 minutes per IP
- Token refresh: 10 per hour per user
- Password reset: 3 per hour per email

## Testing Requirements

### Unit Tests
- JWT token generation/validation
- User creation/retrieval
- Organization creation
- Role checking logic

### Integration Tests
- Complete OAuth flow (mocked Google)
- Token refresh flow
- Account deletion flow

### Security Tests
- Token tampering attempts
- CSRF attack simulation
- Unauthorized access attempts

## Implementation Checklist

- [ ] Set up Google OAuth credentials
- [ ] Implement OAuth callback handler
- [ ] Create user and organization models
- [ ] Implement JWT token generation
- [ ] Add token refresh endpoint
- [ ] Build user profile management
- [ ] Implement organization auto-creation
- [ ] Add RBAC middleware
- [ ] Implement account deletion
- [ ] Add security measures (rate limiting, CSRF)
- [ ] Write comprehensive tests
- [ ] Document API endpoints

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/auth/google/login` | Initiate Google OAuth | No |
| POST | `/api/auth/google/callback` | Handle OAuth callback | No |
| POST | `/api/auth/refresh` | Refresh access token | No (refresh token) |
| POST | `/api/auth/logout` | Logout user | Yes |

### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me` | Get current user | Yes |
| PUT | `/api/users/me` | Update profile | Yes |
| DELETE | `/api/users/me` | Delete account | Yes |
| GET | `/api/users/me/organizations` | List user's orgs | Yes |

### Organization Endpoints

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| GET | `/api/organizations/{id}` | Get org details | Yes | Member |
| PUT | `/api/organizations/{id}` | Update org | Yes | Owner/Admin |
| DELETE | `/api/organizations/{id}` | Delete org | Yes | Owner |
| GET | `/api/organizations/{id}/members` | List members | Yes | Member |
| POST | `/api/organizations/{id}/members` | Invite member | Yes | Owner/Admin |
| DELETE | `/api/organizations/{id}/members/{user_id}` | Remove member | Yes | Owner/Admin |

---

**Next Steps**: Proceed to mode-specific design docs (Brainstorm, Analyze, Implement).

