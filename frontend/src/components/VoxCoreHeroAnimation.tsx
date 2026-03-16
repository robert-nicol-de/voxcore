import React, { useEffect, useState } from "react";
import './VoxCoreHeroAnimation.css';

const nodes = [
  { label: "Query Inspector", icon: "🔍" },
  { label: "Risk Engine", icon: "⚠️" },
  { label: "Policy Engine", icon: "⚖️" },
  { label: "Sandbox Execution", icon: "🧪" },
  { label: "Production Database", icon: "🗄️" }
];

const sqlExample = `SELECT region, SUM(revenue)\nFROM sales\nGROUP BY region`;

const prompt = "What was revenue by region last quarter?";

const riskOverlay = {
  tables: "sales",
  sensitive: "none",
  status: "Approved"
};

export default function VoxCoreHeroAnimation() {
  const [activeNode, setActiveNode] = useState(0);
  const [showRisk, setShowRisk] = useState(false);
  const [showSandbox, setShowSandbox] = useState(false);
  const [showShield, setShowShield] = useState(false);

  useEffect(() => {
    let t1 = setTimeout(() => setActiveNode(1), 800);
    let t2 = setTimeout(() => setActiveNode(2), 1600);
    let t3 = setTimeout(() => setActiveNode(3), 2400);
    let t4 = setTimeout(() => { setActiveNode(4); setShowRisk(true); }, 3200);
    let t5 = setTimeout(() => { setShowRisk(false); setShowSandbox(true); }, 4000);
    let t6 = setTimeout(() => { setShowSandbox(false); setShowShield(true); }, 4800);
    let t7 = setTimeout(() => { setShowShield(false); setActiveNode(0); }, 5600);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); clearTimeout(t5); clearTimeout(t6); clearTimeout(t7); };
  }, [activeNode]);

  return (
    <div className="voxcore-hero-bg">
      <div className="hero-left">
        <div className="prompt-box">
          <span className="prompt-label">User Prompt</span>
          <span className="prompt-text">{prompt}</span>
        </div>
        <div className="sql-box">
          <span className="sql-label">AI Generated SQL</span>
          <pre className="sql-text">{sqlExample}</pre>
        </div>
      </div>
      <div className="hero-center">
        <div className="vc-logo-core">
          {/* Replace with SVG VC logo for production */}
          <span className="vc-logo-symbol">VC</span>
        </div>
        <div className="data-flow-line"></div>
        <div className="inspection-nodes">
          {nodes.map((node, idx) => (
            <div className={`inspection-node${activeNode === idx ? ' active' : ''}`} key={node.label}>
              <span className="node-icon">{node.icon}</span>
              <span className="node-label">{node.label}</span>
              {activeNode === idx && idx === 4 && showShield && <div className="shield-icon">🛡️</div>}
            </div>
          ))}
        </div>
        {showRisk && (
          <div className="risk-overlay">
            <div>Risk Analysis</div>
            <div>Tables Accessed: <b>{riskOverlay.tables}</b></div>
            <div>Sensitive Fields: <b>{riskOverlay.sensitive}</b></div>
            <div>Policy Status: <span className="approved">{riskOverlay.status}</span></div>
            <div className="green-check">✔</div>
          </div>
        )}
        {showSandbox && (
          <div className="sandbox-container">
            <div className="sandbox-title">Sandbox Execution</div>
            <div className="sandbox-db">🗄️</div>
            <div className="sandbox-chart">
              <div className="bar bar1"></div>
              <div className="bar bar2"></div>
              <div className="bar bar3"></div>
            </div>
            <div className="sandbox-rows">Rows: <b>142</b></div>
          </div>
        )}
      </div>
      <div className="hero-right">
        <div className="hero-headline">The Governance Layer<br />for AI-Driven Databases</div>
        <div className="hero-subtext">Inspect, validate, and control every AI-generated query<br />before it reaches production.</div>
        <div className="hero-cta">
          <button className="btn-primary">Launch VoxCloud</button>
          <button className="btn-secondary">Open VoxCore Playground</button>
        </div>
      </div>
    </div>
  );
}
