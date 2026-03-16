export default function PolicyCard({ rule, condition, action }) {
  return (
    <div className="policy-card">
      <h4>{rule}</h4>
      <p>{condition}</p>
      <strong>{action}</strong>
    </div>
  );
}
