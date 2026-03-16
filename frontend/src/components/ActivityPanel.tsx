import React from "react";
import './ActivityPanel.css';
const ActivityPanel: React.FC = () => (
  <footer className="activity-panel">
    <div className="activity-title">Activity / Logs / AI Insights</div>
    {/* Example log entries */}
    <ul className="activity-list">
      <li>12:04 Query blocked (DROP TABLE)</li>
      <li>12:02 Sensitive column accessed</li>
      <li>11:58 Unusual query spike detected</li>
    </ul>
  </footer>
);
export default ActivityPanel;
