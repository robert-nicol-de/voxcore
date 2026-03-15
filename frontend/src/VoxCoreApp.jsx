// VoxCore Chat + Dashboard UI (React)
// This is a high-level scaffold for a magical conversational analytics UI.
// - Left: Chat with VoxCore (WebSocket or REST API)
// - Right: Live Data Intelligence Dashboard (auto-updating)

import React, { useState } from 'react';
import ChatPanel from './ChatPanel';
import DashboardPanel from './DashboardPanel';
import './VoxCoreApp.css';

export default function VoxCoreApp() {
  const [sessionId, setSessionId] = useState(() => Math.random().toString(36).slice(2));
  const [dashboardData, setDashboardData] = useState({});

  // Optionally, use WebSocket for real-time dashboard updates

  return (
    <div className="voxcore-app-layout">
      <div className="chat-panel">
        <ChatPanel sessionId={sessionId} onDashboardUpdate={setDashboardData} />
      </div>
      <div className="dashboard-panel">
        <DashboardPanel data={dashboardData} sessionId={sessionId} />
      </div>
    </div>
  );
}

// ChatPanel: handles user input, sends to /api/conversation/message, displays chat history and suggestions
// DashboardPanel: fetches and displays insights, anomalies, trends, root cause graphs, suggestions
// Use ECharts/Chart.js for charts, D3.js for root cause graphs, and WebSocket for live updates
