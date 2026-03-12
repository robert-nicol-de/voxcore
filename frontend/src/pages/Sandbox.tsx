import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import QuerySandbox from '../components/QuerySandbox';
import EmptyState from '../components/EmptyState';
import { apiUrl } from '../lib/api';

export default function Sandbox() {
  const [loading, setLoading] = useState(true);
  const [hasActivity, setHasActivity] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const loadActivity = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
      try {
        const response = await fetch(apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`));
        if (!response.ok) {
          setHasActivity(true);
          return;
        }
        const data = await response.json();
        setHasActivity(Array.isArray(data?.logs) && data.logs.length > 0);
      } catch {
        setHasActivity(true);
      } finally {
        setLoading(false);
      }
    };

    loadActivity();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--platform-muted)' }}>Loading sandbox...</div>;
  }

  if (!hasActivity) {
    return (
      <EmptyState
        title="Run your first sandbox query"
        message="Use the SQL Assistant to generate a query and preview the results safely in the sandbox."
        variant="fullPage"
        action={<button className="primary-btn" onClick={() => navigate('/app')}>Open SQL Assistant</button>}
      />
    );
  }

  return <QuerySandbox />;
}
