import React from 'react';
import { QueryHistory } from '../components/QueryHistory';

export default function QueryLogs() {
  return (
    <div style={{ padding: 16 }}>
      <h1 style={{ marginTop: 0 }}>Query Logs</h1>
      <QueryHistory />
    </div>
  );
}
