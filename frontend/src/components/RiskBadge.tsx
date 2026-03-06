import React from 'react';
import './RiskBadge.css';

interface RiskBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function RiskBadge({ score, size = 'md', showLabel = true }: RiskBadgeProps) {
  const getStyle = (score: number) => {
    if (score >= 70) {
      return {
        color: 'var(--risk-danger)',
        label: 'Danger',
        emoji: '🔴',
        bgColor: 'rgba(220, 38, 38, 0.1)',
      };
    }
    if (score >= 30) {
      return {
        color: 'var(--risk-warning)',
        label: 'Warning',
        emoji: '🟠',
        bgColor: 'rgba(245, 158, 11, 0.1)',
      };
    }
    return {
      color: 'var(--risk-safe)',
      label: 'Safe',
      emoji: '🟢',
      bgColor: 'rgba(22, 163, 74, 0.1)',
    };
  };

  const style = getStyle(score);

  return (
    <div
      className={`risk-badge risk-badge-${size}`}
      style={{
        borderColor: style.color,
        backgroundColor: style.bgColor,
      }}
    >
      <span className="risk-emoji">{style.emoji}</span>
      <span className="risk-score">{score}</span>
      {showLabel && <span className="risk-label">{style.label}</span>}
    </div>
  );
}
