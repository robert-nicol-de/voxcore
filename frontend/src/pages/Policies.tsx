import React, { useEffect, useState } from 'react';
import { PoliciesManager } from '../components/PoliciesManager';
import EmptyState from '../components/EmptyState';
import { apiUrl, isApiNotFound } from '../lib/api';

export default function Policies() {
  const [isLoading, setIsLoading] = useState(true);
  const [isEmpty, setIsEmpty] = useState(false);
  const [showManager, setShowManager] = useState(false);

  useEffect(() => {
    const loadPolicyPresence = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      try {
        const response = await fetch(apiUrl(`/api/v1/policies/${companyId}`));
        if (isApiNotFound(response)) {
          setIsEmpty(true);
          return;
        }
        if (!response.ok) {
          setIsEmpty(false);
          return;
        }

        const data = await response.json();
        const hasPolicies = Boolean(data?.policies && Object.keys(data.policies).length > 0);
        setIsEmpty(!hasPolicies);
      } catch {
        setIsEmpty(false);
      } finally {
        setIsLoading(false);
      }
    };

    loadPolicyPresence();
  }, []);

  if (isLoading) {
    return <div style={{ color: 'var(--platform-muted)' }}>Loading policies...</div>;
  }

  if (isEmpty && !showManager) {
    return (
      <EmptyState
        title="No policies configured"
        message="Create rules to block destructive queries, protect sensitive columns, and enforce limits."
        variant="fullPage"
        action={<button className="primary-btn" onClick={() => setShowManager(true)}>Create Policy</button>}
      />
    );
  }

  return <PoliciesManager />;
}
