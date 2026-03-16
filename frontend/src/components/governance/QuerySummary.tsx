export default function QuerySummary({ tables, sensitive, risk }) {
  return (
    <div className="query-summary">
      <p>Tables: {tables.join(", ")}</p>
      <p>Sensitive: {sensitive || "None"}</p>
      <p>Risk: {risk}</p>
    </div>
  );
}
