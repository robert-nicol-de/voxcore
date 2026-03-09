import React, { useState, useEffect } from 'react';

interface ThreatEvent {
  time: string;
  message: string;
  level: 'info' | 'warning' | 'critical';
  connector?: string;
}

export const ThreatMonitor: React.FC = () => {
  const [events, setEvents] = useState<ThreatEvent[]>([]);
  const [eventCount, setEventCount] = useState(0);

  useEffect(() => {
    const simulatedEvents: Omit<ThreatEvent, 'time'>[] = [
      { message: 'SQL Injection attempt blocked', level: 'critical', connector: 'sales_db' },
      { message: 'PII table access prevented', level: 'warning', connector: 'hr_db' },
      { message: 'Query exceeded row limit (5000 rows requested)', level: 'warning', connector: 'finance_db' },
      { message: 'Connector policy violation detected (block_delete)', level: 'critical', connector: 'hr_db' },
      { message: 'AI query executed successfully', level: 'info', connector: 'sales_db' },
      { message: 'Credential validation passed', level: 'info', connector: 'finance_db' },
      { message: 'DROP TABLE statement blocked by policy', level: 'critical', connector: 'hr_db' },
      { message: 'Multiple failed connection attempts detected', level: 'warning', connector: 'sales_db' },
      { message: 'Firewall analysis: Risk score 0.45 (High)', level: 'critical', connector: 'finance_db' },
      { message: 'Query fingerprint matched known attack pattern', level: 'critical', connector: 'sales_db' },
    ];

    const interval = setInterval(() => {
      const eventTemplate = simulatedEvents[Math.floor(Math.random() * simulatedEvents.length)];
      const time = new Date().toLocaleTimeString('en-US', { hour12: false });

      setEvents((prev) => [
        {
          time,
          message: eventTemplate.message,
          level: eventTemplate.level,
          connector: eventTemplate.connector,
        },
        ...prev.slice(0, 49), // Keep last 50 events
      ]);

      setEventCount((prev) => prev + 1);
    }, 3000); // New event every 3 seconds

    return () => clearInterval(interval);
  }, []);

  const getColor = (level: string): string => {
    if (level === 'critical') return '#ef4444';
    if (level === 'warning') return '#f59e0b';
    return '#22c55e';
  };

  const getIcon = (level: string): string => {
    if (level === 'critical') return '🔴';
    if (level === 'warning') return '🟡';
    return '🟢';
  };

  const getTotalEvents = () => {
    const critical = events.filter((e) => e.level === 'critical').length;
    const warning = events.filter((e) => e.level === 'warning').length;
    const info = events.filter((e) => e.level === 'info').length;
    return { critical, warning, info };
  };

  const stats = getTotalEvents();

  return (
    <div className="threat-monitor">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
          📊 Live Threat Monitor
        </h2>
        <p style={{ fontSize: '14px', color: '#888', marginBottom: '16px' }}>
          Real-time security event stream
        </p>
      </div>

      {/* Event Statistics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <div style={{
          background: 'rgba(34, 197, 94, 0.1)',
          border: '1px solid rgba(34, 197, 94, 0.2)',
          borderRadius: '6px',
          padding: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Info Events</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#22c55e' }}>{stats.info}</div>
        </div>
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          borderRadius: '6px',
          padding: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Warnings</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#f59e0b' }}>{stats.warning}</div>
        </div>
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: '6px',
          padding: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Critical</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#ef4444' }}>{stats.critical}</div>
        </div>
        <div style={{
          background: 'rgba(0, 212, 255, 0.1)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: '6px',
          padding: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Total Events</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#00d4ff' }}>{eventCount}</div>
        </div>
      </div>

      {/* Event Log */}
      <div className="threat-log">
        {events.length === 0 ? (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: '#666',
            fontSize: '14px'
          }}>
            Waiting for security events...
          </div>
        ) : (
          events.map((event, idx) => (
            <div
              key={idx}
              className="threat-entry"
              style={{
                color: getColor(event.level),
                animation: idx === 0 ? 'slideIn 0.3s ease-out' : 'none'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                paddingBottom: '8px',
                marginBottom: '8px'
              }}>
                <span style={{ minWidth: '16px', marginTop: '2px' }}>
                  {getIcon(event.level)}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                      fontSize: '12px',
                      color: '#8892b0',
                      fontFamily: 'monospace',
                      fontWeight: '600'
                    }}>
                      [{event.time}]
                    </span>
                    {event.connector && (
                      <span style={{
                        fontSize: '11px',
                        background: 'rgba(0, 212, 255, 0.15)',
                        color: '#00d4ff',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontFamily: 'monospace'
                      }}>
                        {event.connector}
                      </span>
                    )}
                  </div>
                  <div style={{
                    fontSize: '13px',
                    marginTop: '4px',
                    color: 'inherit'
                  }}>
                    {event.message}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Legend */}
      <div style={{
        marginTop: '20px',
        padding: '12px',
        background: 'rgba(0, 212, 255, 0.08)',
        borderRadius: '6px',
        border: '1px solid rgba(0, 212, 255, 0.2)',
        fontSize: '11px',
        color: '#ccc',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>🟢</span>
          <span><strong>Info:</strong> Normal operations</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>🟡</span>
          <span><strong>Warning:</strong> Policy limits</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>🔴</span>
          <span><strong>Critical:</strong> Threats blocked</span>
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default ThreatMonitor;
