import { useState, useEffect } from 'react';
import { apiUrl } from '../lib/api';

interface TenantInfo {
  tenant_id: string;
  company_name: string;
  subscription_plan: string;
  users: Array<{
    id: string;
    email: string;
    name: string;
    role: string;
  }>;
}

export default function TenantContext() {
  const [tenant, setTenant] = useState<TenantInfo | null>(null);
  const [allTenants, setAllTenants] = useState<string[]>([]);
  const [selectedTenant, setSelectedTenant] = useState<string>('tenant_acme_corp');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch list of all tenants
    const fetchTenants = async () => {
      try {
        const response = await fetch(apiUrl('/api/v1/tenants'));
        if (response.ok) {
          const data = await response.json();
          setAllTenants(data.tenants || []);
          if (data.tenants && data.tenants.length > 0) {
            setSelectedTenant(data.tenants[0]);
          }
        }
      } catch (error) {
        console.error('Failed to fetch tenants:', error);
      }
    };

    fetchTenants();
  }, []);

  useEffect(() => {
    // Fetch selected tenant configuration
    const fetchTenantConfig = async () => {
      setLoading(true);
      try {
        const response = await fetch(apiUrl(`/api/v1/tenants/${selectedTenant}/config`));
        if (response.ok) {
          const data = await response.json();
          setTenant(data);
        }
      } catch (error) {
        console.error('Failed to fetch tenant config:', error);
      } finally {
        setLoading(false);
      }
    };

    if (selectedTenant) {
      fetchTenantConfig();
    }
  }, [selectedTenant]);

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'Enterprise':
        return '#ef4444'; // Red
      case 'Pro':
        return '#f59e0b'; // Orange
      case 'Starter':
        return '#22c55e'; // Green
      default:
        return '#8892b0'; // Gray
    }
  };

  return (
    <div className="tenant-context">
      <div className="tenant-header">
        <h2>👥 Tenant Overview</h2>
      </div>

      <div className="tenant-selector">
        <label>Select Tenant:</label>
        <select
          value={selectedTenant}
          onChange={(e) => setSelectedTenant(e.target.value)}
          disabled={loading}
        >
          {allTenants.map((tenantId) => (
            <option key={tenantId} value={tenantId}>
              {tenantId}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading tenant information...</div>
      ) : tenant ? (
        <>
          <div className="tenant-info-card">
            <div className="info-section">
              <div className="info-label">Tenant ID</div>
              <div className="info-value">{tenant.tenant_id}</div>
            </div>

            <div className="info-section">
              <div className="info-label">Company</div>
              <div className="info-value">{tenant.company_name}</div>
            </div>

            <div className="info-section">
              <div className="info-label">Subscription Plan</div>
              <div className="info-value">
                <span
                  className="plan-badge"
                  style={{ backgroundColor: getPlanBadgeColor(tenant.subscription_plan) }}
                >
                  {tenant.subscription_plan}
                </span>
              </div>
            </div>
          </div>

          <div className="tenant-users-section">
            <h3>Team Members ({tenant.users.length})</h3>
            <div className="users-grid">
              {tenant.users.map((user) => (
                <div key={user.id} className="user-card">
                  <div className="user-name">{user.name}</div>
                  <div className="user-email">{user.email}</div>
                  <div className="user-role" style={{ color: getRoleColor(user.role) }}>
                    {user.role}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="error">Failed to load tenant information</div>
      )}
    </div>
  );
}

function getRoleColor(role: string): string {
  switch (role) {
    case 'admin':
      return '#ef4444'; // Red
    case 'developer':
      return '#3b82f6'; // Blue
    case 'viewer':
      return '#8b5cf6'; // Purple
    default:
      return '#8892b0'; // Gray
  }
}
