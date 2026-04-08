import "./EmptyStateQuery.css";

export default function EmptyStateQuery({ onRunDemo }) {
  return (
    <div className="empty-state-container">
      <div className="empty-state-content">
        <div className="empty-icon">📋</div>
        <h3>No queries yet</h3>
        <p>
          Run your first query to see how VoxCore protects your database from unsafe AI queries
        </p>
        <button className="empty-cta" onClick={onRunDemo}>
          👉 Run Demo Query
        </button>
      </div>
    </div>
  );
}
