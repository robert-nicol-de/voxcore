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
    <div className="threat-monitor flex flex-col gap-6 text-primary">
      <div className="mb-4">
        <h2 className="text-lg font-bold mb-1">📊 Live Threat Monitor</h2>
        <p className="text-muted text-sm mb-3">Real-time security event stream</p>
      </div>

      {/* Event Statistics */}
      <div className="grid gap-3 mb-5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))' }}>
        <div className="bg-success bg-opacity-10 border-success border rounded-sm p-3 text-center">
          <div className="text-xs text-muted mb-1">Info Events</div>
          <div className="text-xl font-bold" style={{ color: '#22c55e' }}>{stats.info}</div>
        </div>
        <div className="bg-warning bg-opacity-10 border-warning border rounded-sm p-3 text-center">
          <div className="text-xs text-muted mb-1">Warnings</div>
          <div className="text-xl font-bold" style={{ color: '#f59e0b' }}>{stats.warning}</div>
        </div>
        <div className="bg-error bg-opacity-10 border-error border rounded-sm p-3 text-center">
          <div className="text-xs text-muted mb-1">Critical</div>
          <div className="text-xl font-bold" style={{ color: '#ef4444' }}>{stats.critical}</div>
        </div>
        <div className="bg-info bg-opacity-10 border-info border rounded-sm p-3 text-center">
          <div className="text-xs text-muted mb-1">Total Events</div>
          <div className="text-xl font-bold" style={{ color: '#00d4ff' }}>{eventCount}</div>
        </div>
      </div>

      {/* Event Log */}
      <div className="threat-log">
        {events.length === 0 ? (
          <div className="p-10 text-center text-muted text-sm">Waiting for security events...</div>
        ) : (
          events.map((event, idx) => (
            <div
              key={idx}
              className="threat-entry"
              style={{ color: getColor(event.level), animation: idx === 0 ? 'slideIn 0.3s ease-out' : 'none' }}
            >
              <div className="flex items-start gap-3 border-b border-default pb-2 mb-2">
                <span className="min-w-[16px] mt-0.5">{getIcon(event.level)}</span>
                <div className="flex-1">
                  <div className="flex gap-2 items-center">
                    <span className="text-xs text-muted font-mono font-semibold">[{event.time}]</span>
                    {event.connector && (
                      <span className="text-xs bg-info bg-opacity-20 text-info px-2 py-0.5 rounded font-mono">
                        {event.connector}
                      </span>
                    )}
                  </div>
                  <div className="text-sm mt-1" style={{ color: 'inherit' }}>{event.message}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Legend */}
      <div className="mt-5 p-3 bg-info bg-opacity-5 rounded-sm border-info border text-xs text-muted grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))' }}>
        <div className="flex items-center gap-2">
          <span>🟢</span>
          <span><strong>Info:</strong> Normal operations</span>
        </div>
        <div className="flex items-center gap-2">
          <span>🟡</span>
          <span><strong>Warning:</strong> Policy limits</span>
        </div>
        <div className="flex items-center gap-2">
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
