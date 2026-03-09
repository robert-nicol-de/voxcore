import React, { useState, useEffect } from 'react';

interface Query {
  id: string;
  prompt: string;
  sql: string;
  status: 'success' | 'error' | 'warning';
  timestamp: string;
  risk_score: number;
}

interface QueriesProps {
  token: string;
}

export const Queries: React.FC<QueriesProps> = ({ token }) => {
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    // TODO: Replace with actual API call
    // fetch('/api/queries', { headers: { 'Authorization': `Bearer ${token}` } })
    //   .then(res => res.ok ? res.json() : Promise.reject(res))
    //   .then(data => {
    //     setQueries(data);
    //     setLoading(false);
    //   })
    //   .catch(() => {
    //     setError('Failed to load queries');
    //     setLoading(false);
    //   });
    
    // Mock data for now
    setQueries([
      {
        id: '1',
        prompt: 'Show me sales trends',
        sql: 'SELECT DATE_TRUNC(\'month\', order_date) AS month, SUM(amount) FROM orders GROUP BY month',
        status: 'success',
        timestamp: '2026-03-09T15:30:00Z',
        risk_score: 12,
      },
      {
        id: '2',
        prompt: 'Revenue by customer',
        sql: 'SELECT customer_name, SUM(revenue) FROM orders GROUP BY customer_name LIMIT 10',
        status: 'success',
        timestamp: '2026-03-09T14:15:00Z',
        risk_score: 18,
      },
    ]);
    setLoading(false);
  }, [token]);

  if (loading) return <div className="view-content"><p>Loading...</p></div>;
  if (error) return <div className="view-content"><p className="error">{error}</p></div>;

  return (
    <div className="view-content">
      <div className="panel">
        <h2>My Queries</h2>
        <p>View your query history and results</p>
        
        {queries.length === 0 ? (
          <p>No queries yet</p>
        ) : (
          <table className="queries-table">
            <thead>
              <tr>
                <th>Prompt</th>
                <th>Status</th>
                <th>Risk Score</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {queries.map((q) => (
                <tr key={q.id}>
                  <td title={q.prompt}>{q.prompt.substring(0, 40)}...</td>
                  <td><span className={`badge badge-${q.status}`}>{q.status}</span></td>
                  <td>{q.risk_score}</td>
                  <td>{new Date(q.timestamp).toLocaleString()}</td>
                  <td><button className="btn btn-small">View</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
