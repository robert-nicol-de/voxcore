import React from "react";
import './InsightCard.css';

const InsightCard: React.FC<{ type: 'risk' | 'info' | 'success'; title: string; message: string }> = ({ type, title, message }) => (
  <div className={`insight-card ${type}`}> 
    <div className="insight-title">{title}</div>
    <div className="insight-message">{message}</div>
  </div>
);
export default InsightCard;
