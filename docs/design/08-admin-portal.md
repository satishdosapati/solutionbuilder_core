# Design Document: Admin Portal

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 02-authentication-user-management.md

## Overview

Admin Portal provides business operations interface for managing users, organizations, subscriptions, viewing analytics, and handling support requests.

## Requirements

### Functional Requirements

1. **User Management**
   - List all users
   - View user details and activity
   - Suspend/activate users
   - View user sessions and conversations

2. **Organization Management**
   - List organizations
   - View organization details
   - Manage members
   - Manually adjust quotas
   - Change subscription tiers

3. **Subscription & Billing**
   - View all subscriptions
   - Manually upgrade/downgrade
   - Handle failed payments
   - View Stripe invoices
   - Process refunds

4. **Analytics & Reporting**
   - User growth metrics
   - Revenue analytics
   - Subscription metrics
   - Feature usage statistics
   - Conversion funnels

5. **Support**
   - View support tickets (if implemented)
   - Access user conversation history
   - Issue resolution tracking

## Access Control

### Admin Roles

```python
# backend/models/admin.py

class AdminRole(Enum):
    SUPER_ADMIN = "super_admin"  # Full access
    ADMIN = "admin"  # User/org management
    SUPPORT = "support"  # View-only, support tools
    ANALYST = "analyst"  # Analytics only
```

### Permission Matrix

| Feature | Super Admin | Admin | Support | Analyst |
|---------|-------------|-------|---------|---------|
| User Management | ✅ | ✅ | View Only | ❌ |
| Organization Management | ✅ | ✅ | View Only | ❌ |
| Subscription Management | ✅ | ✅ | ❌ | ❌ |
| Analytics | ✅ | ✅ | ❌ | ✅ |
| Support Tools | ✅ | ✅ | ✅ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ |

## API Specification

### GET /api/admin/metrics/overview

**Response:**
```json
{
  "total_users": 1250,
  "user_growth_percentage": 12.5,
  "active_organizations": 890,
  "org_growth_percentage": 8.3,
  "monthly_revenue": 25800.50,
  "revenue_growth_percentage": 15.2,
  "active_sessions": 45,
  "session_change_percentage": 5.0,
  "alerts": [
    {
      "severity": "high",
      "message": "Database connections at 85% capacity"
    }
  ],
  "revenue_data": {
    "this_month": 25800.50,
    "last_month": 22350.00,
    "trend": "up"
  },
  "user_growth_data": [
    {"date": "2024-01-01", "count": 1100},
    {"date": "2024-01-08", "count": 1150},
    {"date": "2024-01-15", "count": 1250}
  ],
  "subscription_breakdown": {
    "free": 850,
    "pro": 380,
    "enterprise": 12
  },
  "top_users": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "sessions_count": 150,
      "last_active": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### GET /api/admin/users

**Query Parameters:**
- `page`, `limit`: Pagination
- `search`: Search by email/name
- `status`: Filter by status

**Response:**
```json
{
  "users": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "User Name",
      "created_at": "2024-01-01T00:00:00Z",
      "last_login_at": "2024-01-15T10:00:00Z",
      "organizations_count": 2,
      "sessions_count": 45,
      "status": "active"
    }
  ],
  "total": 1250,
  "page": 1,
  "limit": 50
}
```

### GET /api/admin/users/{user_id}

**Response:**
```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-15T10:00:00Z",
    "status": "active"
  },
  "organizations": [
    {
      "organization_id": "uuid",
      "name": "User's Workspace",
      "role": "owner",
      "subscription_tier": "pro"
    }
  ],
  "usage_stats": {
    "total_sessions": 45,
    "total_conversations": 120,
    "total_artifacts": 380,
    "storage_used_gb": 2.5
  },
  "recent_activity": [
    {
      "action": "generated_artifacts",
      "timestamp": "2024-01-15T10:00:00Z",
      "details": "Generated CloudFormation template"
    }
  ]
}
```

### POST /api/admin/organizations/{org_id}/upgrade

**Request:**
```json
{
  "tier": "pro",
  "reason": "Customer request"
}
```

**Response:**
```json
{
  "status": "success",
  "organization_id": "uuid",
  "old_tier": "free",
  "new_tier": "pro",
  "effective_date": "2024-01-15T10:00:00Z"
}
```

## Frontend Components

### Admin Dashboard

```typescript
// frontend/admin/pages/Dashboard.tsx
export const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <MetricCard title="Total Users" value={metrics?.total_users} change={metrics?.user_growth_percentage} />
        <MetricCard title="Active Orgs" value={metrics?.active_organizations} change={metrics?.org_growth_percentage} />
        <MetricCard title="Monthly Revenue" value={`$${metrics?.monthly_revenue.toLocaleString()}`} change={metrics?.revenue_growth_percentage} />
        <MetricCard title="Active Sessions" value={metrics?.active_sessions} change={metrics?.session_change_percentage} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <RevenueChart data={metrics?.revenue_data} />
        <UserGrowthChart data={metrics?.user_growth_data} />
      </div>
    </div>
  );
};
```

### User Management

```typescript
// frontend/admin/pages/Users.tsx
export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  return (
    <div className="p-8">
      <div className="flex gap-8">
        {/* User List */}
        <div className="flex-1">
          <UserList users={users} onSelect={setSelectedUser} />
        </div>

        {/* User Details */}
        {selectedUser && (
          <div className="w-96">
            <UserDetails user={selectedUser} />
          </div>
        )}
      </div>
    </div>
  );
};
```

## Implementation Checklist

- [ ] Create admin user model
- [ ] Implement RBAC middleware
- [ ] Build metrics endpoints
- [ ] Create user management endpoints
- [ ] Build organization management endpoints
- [ ] Implement subscription management
- [ ] Create analytics endpoints
- [ ] Build admin dashboard UI
- [ ] Add user management UI
- [ ] Write comprehensive tests

---

**Next Steps**: Proceed to Monitoring Dashboard design doc.

