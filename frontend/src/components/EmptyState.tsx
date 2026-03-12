import React from 'react';

interface Props {
  title: string;
  message: string;
  action?: React.ReactNode;
  variant?: 'default' | 'compact' | 'fullPage';
}

export default function EmptyState({ title, message, action, variant = 'default' }: Props) {
  const variantClass =
    variant === 'compact'
      ? 'empty-state--compact'
      : variant === 'fullPage'
        ? 'empty-state--fullpage'
        : '';

  return (
    <div className={`empty-state ${variantClass}`.trim()}>
      <img
        src="/assets/VC_logo_button.png"
        alt="VoxCore"
        className="empty-logo"
      />

      <h2>{title}</h2>
      <p>{message}</p>

      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}
