import React from "react";

interface Props {
  title: string;
  message?: string;
  suggestions?: string[];
  action?: React.ReactNode;
  variant?: "default" | "compact" | "fullPage";
}

export default function EmptyState({ title, message, suggestions, action, variant = "default" }: Props) {
  const variantClass =
    variant === "compact"
      ? "empty-state--compact"
      : variant === "fullPage"
        ? "empty-state--fullpage"
        : "";

  return (
    <div className={`empty-state ${variantClass}`.trim()}>
      <img
        src="/assets/voxcore-logo-horizontal.svg"
        alt="VoxQuery"
        className="empty-logo"
      />

      <h2>{title}</h2>
      {message && <p>{message}</p>}
      {suggestions && suggestions.length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-[var(--text-secondary)] mb-1">Try:</p>
          <ul className="flex flex-wrap gap-2">
            {suggestions.map((s, i) => (
              <li key={i} className="px-3 py-1 rounded bg-[var(--bg-hover)] text-xs cursor-pointer hover:bg-[var(--bg-elevated)] transition">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}
