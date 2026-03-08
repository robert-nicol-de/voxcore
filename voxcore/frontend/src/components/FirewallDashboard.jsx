"""
AI Firewall Dashboard Widget Component
React component for displaying firewall activity and statistics
"""

const FirewallDashboard = () => {
  const [stats, setStats] = React.useState(null);
  const [recentEvents, setRecentEvents] = React.useState([]);
  const [blockedCount, setBlockedCount] = React.useState(0);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchFirewallData();
    const interval = setInterval(fetchFirewallData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchFirewallData = async () => {
    try {
      const response = await fetch('/api/v1/firewall/dashboard');
      const data = await response.json();
      setStats(data.stats);
      setRecentEvents(data.recent_events || []);
      setBlockedCount(data.blocked_count || 0);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching firewall data:', error);
    }
  };

  if (loading) {
    return <div className="firewall-dashboard loading">Loading firewall data...</div>;
  }

  const blockRate = stats?.block_rate?.toFixed(1) || 0;

  return (
    <div className="firewall-dashboard">
      <div className="firewall-header">
        <h2>🔥 AI Firewall Activity</h2>
        <span className="firewall-status">Active</span>
      </div>

      {/* Stats Cards */}
      <div className="firewall-stats">
        <div className="stat-card">
          <div className="stat-label">Queries Inspected</div>
          <div className="stat-value">{stats?.total_inspected || 0}</div>
        </div>

        <div className="stat-card blocked">
          <div className="stat-label">Blocked</div>
          <div className="stat-value">{stats?.blocked_count || 0}</div>
          <div className="stat-percent">{blockRate}% block rate</div>
        </div>

        <div className="stat-card high-risk">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">{stats?.high_risk_count || 0}</div>
        </div>

        <div className="stat-card medium-risk">
          <div className="stat-label">Medium Risk</div>
          <div className="stat-value">{stats?.medium_risk_count || 0}</div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="firewall-chart">
        <h3>Risk Distribution</h3>
        <div className="risk-bars">
          <div className="risk-bar low">
            <div className="risk-label">Low</div>
            <div className="risk-bar-fill" style={{width: `${(stats?.low_risk_count / stats?.total_inspected * 100) || 0}%`}}>
              {stats?.low_risk_count || 0}
            </div>
          </div>
          <div className="risk-bar medium">
            <div className="risk-label">Medium</div>
            <div className="risk-bar-fill" style={{width: `${(stats?.medium_risk_count / stats?.total_inspected * 100) || 0}%`}}>
              {stats?.medium_risk_count || 0}
            </div>
          </div>
          <div className="risk-bar high">
            <div className="risk-label">High</div>
            <div className="risk-bar-fill" style={{width: `${(stats?.high_risk_count / stats?.total_inspected * 100) || 0}%`}}>
              {stats?.high_risk_count || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Blocked Queries */}
      <div className="firewall-events">
        <h3>Recently Blocked Queries</h3>
        {recentEvents.length === 0 ? (
          <p className="empty-state">No blocked queries detected</p>
        ) : (
          <div className="event-list">
            {recentEvents.filter(e => e.action === 'block').slice(0, 5).map((event, idx) => (
              <div key={idx} className="event-item blocked">
                <div className="event-time">{new Date(event.timestamp).toLocaleTimeString()}</div>
                <div className="event-query">{event.query.substring(0, 60)}...</div>
                <div className="event-violations">
                  {event.violations.map((v, i) => (
                    <span key={i} className="violation-badge">{v}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* High Risk Queries */}
      <div className="firewall-high-risk">
        <h3>High Risk Queries</h3>
        <div className="risk-list">
          {recentEvents.filter(e => e.risk_level === 'HIGH').slice(0, 5).map((event, idx) => (
            <div key={idx} className="risk-item">
              <div className="risk-score">{event.risk_score}</div>
              <div className="risk-details">
                <div className="risk-query">{event.query.substring(0, 50)}...</div>
                <div className="risk-action">Action: {event.action}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .firewall-dashboard {
          padding: 20px;
          background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
          border-radius: 12px;
          color: #eee;
        }

        .firewall-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          border-bottom: 2px solid #ff6b6b;
          padding-bottom: 10px;
        }

        .firewall-header h2 {
          margin: 0;
          font-size: 24px;
        }

        .firewall-status {
          background: #51cf66;
          color: #000;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: bold;
        }

        .firewall-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 15px;
          text-align: center;
        }

        .stat-card.blocked {
          border-color: #ff6b6b;
          background: rgba(255, 107, 107, 0.1);
        }

        .stat-card.high-risk {
          border-color: #ffa94d;
          background: rgba(255, 164, 77, 0.1);
        }

        .stat-card.medium-risk {
          border-color: #ffd43b;
          background: rgba(255, 212, 59, 0.1);
        }

        .stat-label {
          font-size: 12px;
          color: #aaa;
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: #fff;
        }

        .stat-percent {
          font-size: 12px;
          color: #ff6b6b;
          margin-top: 5px;
        }

        .firewall-chart {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 30px;
        }

        .firewall-chart h3 {
          margin-top: 0;
          margin-bottom: 15px;
        }

        .risk-bars {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .risk-bar {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .risk-label {
          width: 60px;
          font-size: 12px;
          font-weight: bold;
        }

        .risk-bar-fill {
          flex: 1;
          height: 30px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding-right: 10px;
          color: #fff;
          font-weight: bold;
          font-size: 12px;
        }

        .risk-bar.low .risk-bar-fill {
          background: #51cf66;
        }

        .risk-bar.medium .risk-bar-fill {
          background: #ffd43b;
          color: #000;
        }

        .risk-bar.high .risk-bar-fill {
          background: #ff6b6b;
        }

        .firewall-events {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 107, 107, 0.3);
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 30px;
        }

        .firewall-events h3 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #ff6b6b;
        }

        .event-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .event-item {
          background: rgba(0, 0, 0, 0.3);
          border-left: 3px solid #ff6b6b;
          padding: 10px;
          border-radius: 4px;
        }

        .event-time {
          font-size: 11px;
          color: #aaa;
        }

        .event-query {
          font-family: monospace;
          font-size: 12px;
          color: #fff;
          margin: 5px 0;
        }

        .event-violations {
          display: flex;
          gap: 5px;
          flex-wrap: wrap;
          margin-top: 5px;
        }

        .violation-badge {
          background: #ff6b6b;
          color: #fff;
          padding: 3px 6px;
          border-radius: 3px;
          font-size: 10px;
        }

        .firewall-high-risk {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 164, 77, 0.3);
          border-radius: 8px;
          padding: 20px;
        }

        .firewall-high-risk h3 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #ffa94d;
        }

        .risk-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .risk-item {
          display: flex;
          gap: 15px;
          background: rgba(0, 0, 0, 0.3);
          padding: 10px;
          border-radius: 4px;
          border-left: 3px solid #ffa94d;
        }

        .risk-score {
          font-size: 20px;
          font-weight: bold;
          color: #ffa94d;
          min-width: 40px;
          text-align: center;
        }

        .risk-details {
          flex: 1;
        }

        .risk-query {
          font-family: monospace;
          font-size: 12px;
          color: #fff;
          margin-bottom: 5px;
        }

        .risk-action {
          font-size: 11px;
          color: #aaa;
        }

        .empty-state {
          text-align: center;
          color: #666;
          padding: 20px;
        }

        .loading {
          text-align: center;
          padding: 40px;
          opacity: 0.7;
        }
      `}</style>
    </div>
  );
};

export default FirewallDashboard;
