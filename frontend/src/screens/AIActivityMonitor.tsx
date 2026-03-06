import React, { useEffect, useState } from 'react';
import { Card, Badge, Input, Button } from '../components';
import './AIActivityMonitor.css';

interface Activity {
  id: string;
  user: string;
  prompt: string;
  generated_sql: string;
  risk_score: number;
  risk_level: 'safe' | 'warning' | 'danger';
  action_taken: 'executed' | 'blocked' | 'rewritten';
  execution_time_ms?: number;
  result_rows?: number;
  blocked_reason?: string;
  rewritten_sql?: string;
  timestamp: string;
}

interface ActivityResponse {
  activities: Activity[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export const AIActivityMonitor: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterUser, setFilterUser] = useState('');
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        let url = '/api/governance/activity/feed?limit=50';
        if (filterUser) url += `&filter_user=${filterUser}`;
        if (filterRiskLevel) url += `&filter_risk_level=${filterRiskLevel}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch activities');
        const data: ActivityResponse = await response.json();
        setActivities(data.activities);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, [filterUser, filterRiskLevel]);

  const getRiskBadgeVariant = (level: string) => {
    switch (level) {
      case 'safe':
        return 'safe';
      case 'warning':
        return 'warning';
      case 'danger':
        return 'danger';
      default:
        return 'info';
    }
  };

  const getActionBadgeVariant = (action: string) => {
    switch (action) {
      case 'executed':
        return 'safe';
      case 'blocked':
        return 'danger';
      case 'rewritten':
        return 'warning';
      default:
        return 'info';
    }
  };

  if (loading) return <div className="monitor-loading">Loading activity feed...</div>;
  if (error) return <div className="monitor-error">Error: {error}</div>;

  return (
    <div className="ai-activity-monitor">
      <h1>AI Activity Monitor</h1>

      {/* Filters */}
      <Card elevation="sm">
        <div className="filter-bar">
          <Input
            value={filterUser}
            onChange={setFilterUser}
            placeholder="Filter by user email..."
            state={filterUser ? 'filled' : 'default'}
          />
          <select
            value={filterRiskLevel}
            onChange={(e) => setFilterRiskLevel(e.target.value)}
            className="filter-select"
          >
            <option value="">All Risk Levels</option>
            <option value="safe">Safe</option>
            <option value="warning">Warning</option>
            <option value="danger">Danger</option>
          </select>
        </div>
      </Card>

      {/* Activity Table */}
      <Card elevation="md">
        <div className="activity-table">
          <div className="table-header">
            <div className="col-user">User</div>
            <div className="col-prompt">Prompt</div>
            <div className="col-risk">Risk</div>
            <div className="col-action">Action</div>
            <div className="col-time">Time</div>
          </div>

          {activities.length === 0 ? (
            <div className="table-empty">No activities found</div>
          ) : (
            activities.map((activity) => (
              <div key={activity.id}>
                <div
                  className="table-row"
                  onClick={() => setExpandedId(expandedId === activity.id ? null : activity.id)}
                >
                  <div className="col-user">{activity.user.split('@')[0]}</div>
                  <div className="col-prompt">{activity.prompt.substring(0, 50)}...</div>
                  <div className="col-risk">
                    <Badge variant={getRiskBadgeVariant(activity.risk_level)}>
                      {activity.risk_score}
                    </Badge>
                  </div>
                  <div className="col-action">
                    <Badge variant={getActionBadgeVariant(activity.action_taken)}>
                      {activity.action_taken}
                    </Badge>
                  </div>
                  <div className="col-time">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </div>
                </div>

                {expandedId === activity.id && (
                  <div className="table-details">
                    <div className="detail-section">
                      <h4>Prompt</h4>
                      <p>{activity.prompt}</p>
                    </div>

                    <div className="detail-section">
                      <h4>Generated SQL</h4>
                      <pre className="sql-code">{activity.generated_sql}</pre>
                    </div>

                    {activity.rewritten_sql && (
                      <div className="detail-section">
                        <h4>Rewritten SQL</h4>
                        <pre className="sql-code">{activity.rewritten_sql}</pre>
                      </div>
                    )}

                    {activity.blocked_reason && (
                      <div className="detail-section error">
                        <h4>Blocked Reason</h4>
                        <p>{activity.blocked_reason}</p>
                      </div>
                    )}

                    {activity.execution_time_ms && (
                      <div className="detail-stats">
                        <div className="stat">
                          <span className="stat-label">Execution Time:</span>
                          <span className="stat-value">{activity.execution_time_ms}ms</span>
                        </div>
                        {activity.result_rows && (
                          <div className="stat">
                            <span className="stat-label">Result Rows:</span>
                            <span className="stat-value">{activity.result_rows}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Export Button */}
      <div className="monitor-actions">
        <Button variant="secondary" onClick={() => alert('Export functionality coming soon')}>
          Export as CSV
        </Button>
      </div>
    </div>
  );
};
