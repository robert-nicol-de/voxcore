export default function Skeleton({ className = "" }) {
  return (
    <div
      className={`animate-pulse bg-[var(--bg-hover)] rounded-md ${className}`}
    />
  );
}
