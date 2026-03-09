import { useState } from "react";
import './DemoMode.css';

export default function DemoMode() {
  const [sql, setSql] = useState("");
  const [firewall, setFirewall] = useState("");
  const [results, setResults] = useState("");

  function runDemo() {
    setSql("Generating SQL...");
    setFirewall("");
    setResults("");

    setTimeout(() => {
      setSql(`SELECT region,\nSUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC`);
    }, 800);

    setTimeout(() => {
      setFirewall(`\n✓ Syntax correct\n✓ No injection risk\n✓ Policy compliant`);
    }, 1600);

    setTimeout(() => {
      setResults(`\nRegion      Revenue\nNorth       $1,250,000\nSouth       $980,000\nWest        $875,000`);
    }, 2400);
  }

  return (
    <div className="demo-container">
      <div className="demo-banner">
        ⚡ DEMO MODE — Connections disabled, preview only
      </div>
      <h1>Try VoxCore</h1>
      <div className="demo-input">
        <input
          placeholder="Ask your database anything..."
          id="demoQuestion"
        />
        <button onClick={runDemo} className="demo-btn">
          Ask VoxCore
        </button>
      </div>
      <pre className="demo-sql">{sql}</pre>
      <pre className="demo-firewall">{firewall}</pre>
      <pre className="demo-results">{results}</pre>
    </div>
  );
}
