export default function Card({ children }: any) {
  return (
    <div className="card bg-[var(--bg-surface)] border border-[var(--border-default)] p-6 rounded-xl transition-all">
      {children}
    </div>
  );
}
