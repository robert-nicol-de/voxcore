import React from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import SemanticModelCreator from '../components/datasources/SemanticModelCreator';

export default function SemanticModelsPage() {
  const navigate = useNavigate();

  return (
    <div>
      <PageHeader
        title="Semantic Models"
        subtitle="Define business entities and metrics for more accurate AI SQL generation"
      />
      <SemanticModelCreator onSaved={() => navigate('/app')} />
    </div>
  );
}
