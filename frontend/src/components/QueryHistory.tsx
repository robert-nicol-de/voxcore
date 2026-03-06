import React, { useState } from 'react';
import './QueryHistory.css';

interface Query {
  id: string;
  timestamp: string;
  question: string;
  sql: string;
  database: string;
  rowsReturned: number;
  executionTime: number;
  status: 'success' | 'error';
}

export const QueryHistory: React.FC = () => {
  const mockQueries: Query[] = [
    {
      id: '1',
      timestamp: '2024-03-01 14:32:15',
      question: 'What are the top 10 products by sales?',
      sql: 'SELECT TOP 10 ProductID, Name, SUM(Quantity) as TotalSales FROM Products p JOIN OrderDetails od ON p.ProductID = od.ProductID GROUP BY p.ProductID, p.Name ORDER BY TotalSales DESC',
      database: 'AdventureWorks2022',
      rowsReturned: 10,
      executionTime: 245,
      status: 'success',
    },
    {
      id: '2',
      timestamp: '2024-03-01 14:28:42',
      question: 'Show me customer orders from last month',
      sql: 'SELECT c.CustomerID, c.CompanyName, COUNT(o.OrderID) as OrderCount FROM Customers c LEFT JOIN Orders o ON c.CustomerID = o.CustomerID WHERE o.OrderDate >= DATEADD(MONTH, -1, GETDATE()) GROUP BY c.CustomerID, c.CompanyName',
      database: 'AdventureWorks2022',
      rowsReturned: 45,
      executionTime: 312,
      status: 'success',
    },
    {
      id: '3',
      timestamp: '2024-03-01 14:15:08',
      question: 'What is the average order value?',
      sql: 'SELECT AVG(TotalDue) as AverageOrderValue FROM Orders',
      database: 'AdventureWorks2022',
      rowsReturned: 1,
      executionTime: 89,
      status: 'success',
    },
    {
      id: '4',
      timestamp: '2024-03-01 13:52:33',
      question: 'List all employees and their departments',
      sql: 'SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName FROM Employees e JOIN Departments d ON e.DepartmentID = d.DepartmentID ORDER BY d.DepartmentName, e.LastName',
      database: 'AdventureWorks2022',
      rowsReturned: 290,
      executionTime: 156,
      status: 'success',
    },
    {
      id: '5',
      timestamp: '2024-03-01 13:28:19',
      question: 'Invalid query test',
      sql: 'SELECT * FROM NonExistentTable',
      database: 'AdventureWorks2022',
      rowsReturned: 0,
      executionTime: 0,
      status: 'error',
    },
  ];

  const [queries] = useState<Query[]>(mockQueries);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="query-history">
      <div className="history-header">
        <h1>Query History</h1>
        <p className="history-subtitle">View and manage your previous queries</p>
      </div>

      <div className="history-stats">
        <div className="stat-card">
          <div className="stat-label">Total Queries</div>
          <div className="stat-value">{queries.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Successful</div>
          <div className="stat-value">{queries.filter(q => q.status === 'success').length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Failed</div>
          <div className="stat-value">{queries.filter(q => q.status === 'error').length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Execution</div>
          <div className="stat-value">
            {Math.round(queries.filter(q => q.status === 'success').reduce((sum, q) => sum + q.executionTime, 0) / queries.filter(q => q.status === 'success').length)}ms
          </div>
        </div>
      </div>

      <div className="history-list">
        {queries.map((query) => (
          <div key={query.id} className="history-item">
            <div className="item-header" onClick={() => toggleExpand(query.id)}>
              <div className="item-left">
                <div className={`status-indicator ${query.status}`}></div>
                <div className="item-info">
                  <div className="item-question">{query.question}</div>
                  <div className="item-meta">
                    <span className="meta-time">⏱ {query.timestamp}</span>
                    <span className="meta-db">🗄️ {query.database}</span>
                    <span className="meta-rows">📊 {query.rowsReturned} rows</span>
                    <span className="meta-time">⚡ {query.executionTime}ms</span>
                  </div>
                </div>
              </div>
              <div className="expand-icon">{expandedId === query.id ? '▼' : '▶'}</div>
            </div>

            {expandedId === query.id && (
              <div className="item-details">
                <div className="sql-block">
                  <div className="sql-label">Generated SQL:</div>
                  <pre className="sql-code">{query.sql}</pre>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
