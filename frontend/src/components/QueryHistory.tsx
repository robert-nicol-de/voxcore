import React, { useState } from 'react';

interface HistoryItem {
  fingerprint: string;
  query: string;
  time: string;
}

export const QueryHistory: React.FC = () => {
  const [history] = useState<HistoryItem[]>([
    {
      fingerprint: '7d31f91c',
      query: 'SELECT region, SUM(revenue) FROM sales GROUP BY region',
      time: '2 min ago',
    },
    {
      fingerprint: '991a3ff2',
      query: 'SELECT COUNT(*) FROM accounts',
      time: '5 min ago',
    },
    {
      fingerprint: 'b2ac4aa1',
      query: 'SELECT * FROM transactions LIMIT 50',
      time: '10 min ago',
    },
  ]);

  return (
    <div className="query-history">
      <h2>📜 Query History</h2>

      <ul>
        {history.map((item, index) => (
          <li key={index}>
            <div className="history-row">
              <span className="fingerprint">{item.fingerprint}</span>
              <span className="query">{item.query}</span>
              <span className="time">{item.time}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
