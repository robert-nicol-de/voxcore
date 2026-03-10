import React, { useEffect, useState } from 'react';
import '../styles/DevSpace.css';
import { isAdmin, isDeveloper, getRoleLabel } from '../utils/permissions';
import DevSidebar from '../components/DevSidebar';
import SecurityShield from '../components/SecurityShield';
import ProtectionRules from '../components/ProtectionRules';
import AttackSimulator from '../components/AttackSimulator';
import QuerySandbox from '../components/QuerySandbox';
import { SchemaMap } from '../components/SchemaMap';
import { QueryInspector } from '../components/QueryInspector';
import { QueryMetrics } from '../components/QueryMetrics';
import { QueryHistory } from '../components/QueryHistory';
import { ConnectorsPanel } from '../components/ConnectorsPanel';
import { ConnectorSecurity } from '../components/ConnectorSecurity';
import { ThreatMonitor } from '../components/ThreatMonitor';
import SecurityScore from '../components/SecurityScore';
import TenantContext from '../components/TenantContext';
import ZeroTrustPolicy from '../components/ZeroTrustPolicy';
import { apiUrl } from '../lib/api';

interface DevSpaceProps {
  token: string;
}

export const DevSpace: React.FC<DevSpaceProps> = ({ token }) => {
  const [userRole, setUserRole] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState<string>('dashboard');

  // Fetch user role from /auth/me endpoint
  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const response = await fetch(apiUrl('/api/v1/auth/me'), {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const user = await response.json();
          setUserRole(user.role);
        }
      } catch (error) {
        console.error('Failed to fetch user role:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchUserRole();
    }
  }, [token]);

  if (loading) {
    return (
      <div className="dev-layout">
        <DevSidebar currentView={currentView} setView={setCurrentView} />
        <div className="dev-main">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Check access: admin (god/admin) + developer can access
  if (!isAdmin(userRole) && !isDeveloper(userRole)) {
    return (
      <div className="dev-layout">
        <DevSidebar currentView={currentView} setView={setCurrentView} />
        <div className="dev-main">
          <div className="access-denied">
            <h2>🔒 Access Denied</h2>
            <p>Developer Space is only available to Admin and Developer users.</p>
            <p>Your role: <strong>{getRoleLabel(userRole)}</strong></p>
          </div>
        </div>
      </div>
    );
  }

  function renderView() {
    switch (currentView) {
      case 'tenants':
        return <TenantContext />
      case 'zerotrust':
        return <ZeroTrustPolicy />
      case 'sandbox':
        return <QuerySandbox />
      case 'inspector':
        return <QueryInspector />
      case 'schema':
        return <SchemaMap />
      case 'connectors':
        return <ConnectorsPanel />
      case 'connectorsecurity':
        return <ConnectorSecurity />
      case 'threatmonitor':
        return <ThreatMonitor />
      case 'security':
        return <SecurityShield />
      case 'rules':
        return <ProtectionRules />
      case 'attacks':
        return <AttackSimulator />
      case 'history':
        return <QueryHistory />
      case 'metrics':
        return <QueryMetrics />
      default:
        return (
          <>
            <SecurityScore />
            <SecurityShield />
            <ConnectorSecurity />
          </>
        )
    }
  }

  return (
    <div className="dev-layout">
      <DevSidebar currentView={currentView} setView={setCurrentView} />
      <div className="dev-main">
        {renderView()}
      </div>
    </div>
  );
};
