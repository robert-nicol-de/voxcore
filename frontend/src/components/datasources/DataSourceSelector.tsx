import React from 'react';
import { useNavigate } from 'react-router-dom';

export type SourceStatus = 'active' | 'coming';

export type DataSourceCard = {
  id: string;
  name: string;
  subtitle: string;
  icon: string;
  status: SourceStatus;
};

const sources: DataSourceCard[] = [
  { id: 'snowflake', name: 'Snowflake', subtitle: 'Cloud DW', icon: '❄', status: 'active' },
  { id: 'semantic', name: 'Semantic Model', subtitle: 'AI Layer', icon: '🧠', status: 'active' },
  { id: 'sqlserver', name: 'SQL Server', subtitle: 'Microsoft DB', icon: '🗄', status: 'active' },
  { id: 'postgres', name: 'PostgreSQL', subtitle: 'Open Source', icon: '🐘', status: 'coming' },
  { id: 'redshift', name: 'Redshift', subtitle: 'AWS DW', icon: '📦', status: 'coming' },
  { id: 'bigquery', name: 'BigQuery', subtitle: 'Google DW', icon: '🌐', status: 'coming' },
];

type Props = {
  onClose?: () => void;
};

export default function DataSourceSelector({ onClose }: Props) {
  const navigate = useNavigate();

  const handleClick = (source: DataSourceCard) => {
    if (source.status !== 'active') return;
    if (source.id === 'semantic') {
      navigate('/app/semantic-models/new');
      return;
    }
    navigate(`/datasources/new/${source.id}`);
  };

  return (
    <div>
      <div className="datasource-selector-header">
        <h2>Add Data Source</h2>
        <p>Connect a database or AI semantic model.</p>
      </div>

      <div className="selector-label">Select Platform</div>

      <div className="datasource-grid">
        {sources.map((s) => (
          <div
            key={s.id}
            className={`source-card ${s.status}`}
            onClick={() => handleClick(s)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleClick(s);
              }
            }}
          >
            <div className="source-icon">{s.icon}</div>
            <h3>{s.name}</h3>
            <div className="source-subtitle">{s.subtitle}</div>
            {s.status === 'coming' && <span className="coming-badge">Coming Soon</span>}
          </div>
        ))}
      </div>

      <div className="selector-actions">
        <button className="secondary-btn" onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
