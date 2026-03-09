# VoxCore Role-Based Access Control (RBAC)

Complete documentation of the role-based permission system for VoxCore.

## Role Hierarchy

```
┌─────────────────────┐
│   GOD (100)         │  ← Platform owner / Super admin
│   Full control      │
└─────────────────────┘
           ↓
┌─────────────────────┐
│   ADMIN (80)        │  ← Company admin
│   Full C ompany     │  
│   control           │
└─────────────────────┘
           ↓
┌─────────────────────┐
│  DEVELOPER (60)     │  ← Dev tools + queries
│  Dev + Schema       │
└─────────────────────┘
           ↓
┌─────────────────────┐
│   ANALYST (40)      │  ← Queries only
│   Run queries       │
└─────────────────────┘
           ↓
┌─────────────────────┐
│   VIEWER (20)       │  ← Dashboards only
│   View dashboards   │
└─────────────────────┘
```

## Feature Access Matrix

| Feature | God | Admin | Dev | Analyst | Viewer |
|---------|-----|-------|-----|---------|--------|
| **Run Queries** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Dev Space** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Firewall Rules** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Manage Users** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Schema Explorer** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Governance** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Admin Panel** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **View Dashboards** | ✅ | ✅ | ✅ | ✅ | ✅ |

## Frontend Implementation

### Location
- `frontend/src/utils/permissions.ts` - All permission checks and helpers

### Core Functions

```typescript
// Check if user is admin (god or admin)
isAdmin(role: string): boolean

// Check if user can access developer tools
isDeveloper(role: string): boolean

// Check if user can run queries
canRunQueries(role: string): boolean

// Check if user can access dashboards
canAccessDashboards(role: string): boolean

// Get human-readable role label
getRoleLabel(role: string): string  // "🌟 God Admin" etc

// Get feature access map
getFeatureAccess(role: string): FeatureAccess
```

### Usage Example

```typescript
import { isAdmin, isDeveloper } from '../utils/permissions'

// In a component:
if (!isAdmin(userRole) && !isDeveloper(userRole)) {
  return <div>Access denied</div>
}

// Show Dev Space button only for allowed roles:
{(isAdmin(userRole) || isDeveloper(userRole)) && (
  <button>Dev Space ⚙️</button>
)}
```

## Backend Implementation

### Location
- `voxcore/voxquery/voxquery/api/permissions.py` - All permission checks and helpers
- `voxcore/voxquery/voxquery/api/models.py` - User model with role hierarchy

### Core Functions

```python
# Check if user is admin
is_admin(user: User) -> bool

# Check if user can access dev tools
is_developer(user: User) -> bool

# Check if user can run queries
can_run_queries(user: User) -> bool

# Require admin - raises HTTPException if not admin
require_admin(user: User) -> User

# Require dev access - raises HTTPException if not developer
require_dev(user: User) -> User

# Require query access
require_query_access(user: User) -> User

# Get feature access map
get_feature_access(user: User) -> dict
```

### Usage Example

```python
from .permissions import require_admin, is_developer
from .models import User

@router.post("/admin/firewall")
async def update_firewall(data: dict, request: Request):
    """Only admin/god can update firewall rules."""
    db = SessionLocal()
    try:
        user = _get_current_user(request, db)
        require_admin(user, "Only admins can update firewall rules")
        
        # ... update firewall logic ...
        return {"success": True}
    finally:
        db.close()


@router.get("/dev/schema")
async def get_schema(request: Request):
    """Only developers/admins/god can access schema."""
    db = SessionLocal()
    try:
        user = _get_current_user(request, db)
        if not is_developer(user):
            raise HTTPException(status_code=403, detail="Developer access required")
        
        # ... schema logic ...
        return schema_data
    finally:
        db.close()
```

## UI Components

### RoleBadge Component
- Location: `frontend/src/components/RoleBadge.tsx`
- Shows color-coded role badge
- Supports compact mode for tables

```tsx
<RoleBadge role={user.role} />  // Full badge
<RoleBadge role={user.role} compact />  // Compact badge
```

### Role Display Locations
- UserDropdown: Shows role badge in dropdown menu
- Profile page: Shows role with badge
- Admin Users table: Shows compact role badges

## Multi-Tenant Considerations

When VoxCore becomes multi-tenant SaaS:

```
Platform (God user)
  ├─── Company A
  │    ├─ Admin
  │    ├─ Developer
  │    ├─ Analyst
  │    └─ Viewer
  │
  └─── Company B
       ├─ Admin
       ├─ Developer
       └─ Viewer
```

- **God** users: See & control everything across all companies
- **Admin** users: Control only their own company
- **Developer/Analyst/Viewer**: Work only within their company

## Admin Bypass Logic

Admin users (god/admin) automatically bypass restrictions on their tier:

```
Feature: "Run Query"
- If user is Viewer → ❌ Deny
- If user is Admin or God → ✅ Always allow (bypass)
- If user is Analyst → ✅ Allow
- If user is Developer → ✅ Allow
```

## Environment Variables

No env vars needed for RBAC - roles are determined by database user records.

## Testing Roles

Create test users with different roles:

```python
# In add_god_user_standalone.py or equivalent:
user = User(
    email="test@company.com",
    name="Test User",
    password_hash=hash_password("password"),
    company_id=1,
    role="developer",  # Set role here
    status="active"
)
```

## Security Notes

1. **Always validate on backend** - Frontend checks are UI only
2. **Use require_* functions** - These raise HTTPException if permission denied
3. **Check on every endpoint** - Don't rely on frontend permission checks
4. **Log access attempts** - Log failed auth/permission checks
5. **Admin bypass is intentional** - Admins need override capability

## Future Improvements

- [ ] Add resource-level permissions (query specific tables)
- [ ] Add time-based access (access until date X)
- [ ] Add IP whitelist/blacklist
- [ ] Add API key scopes
- [ ] Add audit trail for permission changes
- [ ] Add permission groups for bulk assignment
