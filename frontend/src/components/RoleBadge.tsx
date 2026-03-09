import React from 'react';
import './RoleBadge.css';
import { getRoleLabel, getRoleBadgeColor } from '../utils/permissions';

interface RoleBadgeProps {
  role?: string;
  compact?: boolean;
}

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role, compact = false }) => {
  if (!role) return null;

  const label = getRoleLabel(role);
  const color = getRoleBadgeColor(role);

  if (compact) {
    return (
      <span 
        className="role-badge-compact"
        style={{ borderColor: color, color: color }}
        title={label}
      >
        {role.toUpperCase()}
      </span>
    );
  }

  return (
    <div 
      className="role-badge"
      style={{ 
        borderColor: color,
        backgroundColor: `${color}15`
      }}
    >
      <span className="role-badge-label" style={{ color }}>
        {label}
      </span>
    </div>
  );
};
