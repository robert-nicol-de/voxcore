import React, { useState, useEffect } from "react";
import Table from "../components/Table";

interface Query {
  id: string;
  prompt: string;
  sql: string;
  status: "success" | "error" | "warning";
  timestamp: string;
  risk_score: number;
}

interface QueriesProps {
  token: string;
}

export const Queries: React.FC<QueriesProps> = ({ token }) => {
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
        id: "1",
        prompt: "Show me sales trends",
        sql: "SELECT DATE_TRUNC('month', order_date) AS month, SUM(amount) FROM orders GROUP BY month",
        status: "success",
        timestamp: "2026-03-09T15:30:00Z",
        risk_score: 12,
      },
      {
        id: "2",
        prompt: "Revenue by customer",
        sql: "SELECT customer_name, SUM(revenue) FROM orders GROUP BY customer_name LIMIT 10",
        status: "success",
        timestamp: "2026-03-09T14:15:00Z",
        risk_score: 18,
      },
    ]);
    setLoading(false);
  }, [token]);

  if (loading) return <SkeletonTable />;
  if (error) return <div className="view-content"><p className="error">{error}</p></div>;

  return (
    <div className="view-content">
      <div className="panel">
        <h2>My Queries</h2>
        <p>View your query history and results</p>
        
        <Table data={queries} loading={loading} />
      </div>
    </div>
  );
};
