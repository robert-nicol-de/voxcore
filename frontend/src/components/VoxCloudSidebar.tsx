import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/app/dashboard', label: 'Dashboard' },
  { to: '/app/databases', label: 'Databases' },
  { to: '/app', label: 'SQL Assistant' },
  { to: '/app/policies', label: 'Policies' },
  { to: '/app/query-logs', label: 'Query Logs' },
  { to: '/app/sandbox', label: 'Sandbox' },
];

export const VoxCloudSidebar: React.FC = () => {
  const location = useLocation();

  return (
    <aside
      style={{
        width: 240,
        minHeight: '100vh',
        background: '#0b1220',
        borderRight: '1px solid rgba(255,255,255,0.08)',
        padding: '22px 18px',
      }}
    >
      <div style={{ fontSize: 24, fontWeight: 700, color: '#93c5fd', marginBottom: 20 }}>VoxCloud</div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {links.map((item) => {
          const active = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              style={{
                color: active ? '#0f172a' : '#cbd5e1',
                textDecoration: 'none',
                background: active ? '#93c5fd' : 'transparent',
                border: active ? '1px solid #93c5fd' : '1px solid rgba(255,255,255,0.08)',
                borderRadius: 10,
                padding: '10px 12px',
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
