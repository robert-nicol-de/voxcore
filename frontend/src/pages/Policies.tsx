import React, { useEffect, useState } from 'react';
import { PoliciesManager } from '../components/PoliciesManager';
import EmptyState from '../components/EmptyState';
import PageHeader from '../components/PageHeader';
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
    return (
      <div className="flex flex-col gap-4">
        <PageHeader title="Policies" subtitle="AI Security Rules and Enforcement Controls" />
        <div className="text-muted">Loading policies...</div>
      </div>
    );
  }

  if (isEmpty && !showManager) {
    return (
      <div className="flex flex-col gap-4">
        <PageHeader title="Policies" subtitle="AI Security Rules and Enforcement Controls" />
        <EmptyState
          title="No policies configured"
          message="Create rules to block destructive queries, protect sensitive columns, and enforce limits."
          variant="fullPage"
          action={<button className="primary-btn" onClick={() => setShowManager(true)}>Create Policy</button>}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Policies" subtitle="AI Security Rules and Enforcement Controls" />
      <PoliciesManager />
    </div>
  );
}
