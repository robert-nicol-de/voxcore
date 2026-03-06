import React from 'react';
import './RiskBadge.css';

export default function RiskBadge({ level, score }) {
  const config = {
    safe: {
      label: 'Safe',
      icon: '✓',
      className: 'risk-badge-safe',
    },
    warning: {
      label: 'Warning',
      icon: '⚠',
      className: 'risk-badge-warning',
    },
    danger: {
      label: 'Danger',
      icon: '✕',
      className: 'risk-badge-danger',
    },
  };

  const { label, icon, className } = config[level] || config.safe;

  return (
    <span className={`risk-badge ${className}`}>
      <span className="risk-icon">{icon}</span>
      <span className="risk-label">{label}</span>
      {score !== undefined && <span className="risk-score">{score}</span>}
    </span>
  );
}
