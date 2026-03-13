import React, { useState } from 'react';
import PageHeader from '../components/PageHeader';

// ── Layer data ──────────────────────────────────────────────────────────────

const LAYERS = [
  {
    id: 'ui',
    number: '01',
    label: 'User Interface Layer',
    sublabel: 'React Platform',
    color: '#4f8cff',
    border: 'rgba(79,140,255,0.35)',
    bg: 'rgba(79,140,255,0.06)',
    icon: '🖥',
    description:
      'The control center. Renders AI analytics, governance alerts, and approval workflows. Every user action flows downward to the intelligence layer.',
    modules: [
      'SQL Assistant',
      'Governance Dashboard',
      'Query Explorer',
      'Policy Manager',
      'Data Source Manager',
      'Workspace Switcher',
    ],
    capabilities: [
      'Natural language analytics',
      'Visualization rendering (ECharts)',
      'Governance alerts & approval workflows',
      'Schema Explorer',
      'Query Activity Monitor',
    ],
    flow: 'User asks question → UI sends prompt to API → Results + Charts + Insights rendered',
  },
  {
    id: 'ai',
    number: '02',
    label: 'AI Intelligence Layer',
    sublabel: 'The VoxCore Brain',
    color: '#a78bfa',
    border: 'rgba(167,139,250,0.35)',
    bg: 'rgba(167,139,250,0.06)',
    icon: '🧠',
    description:
      'Where analytical reasoning lives. VoxCore reasons before generating SQL — mapping business questions to semantic metrics, analytical plans, and query graphs.',
    modules: [
      'Intent Detection',
      'Semantic Brain',
      'Query Graph Builder',
      'Analytical Planner',
      'Visualization Engine',
      'Insight Engine',
    ],
    capabilities: [
      'Understand business questions',
      'Map to semantic metrics & dimensions',
      'Generate analytical plans',
      'Build deterministic query graphs',
      'Recommend charts & generate insights',
      'Hypothesis & pattern detection',
    ],
    flow: 'Prompt → Intent Parser → Semantic Model Lookup → Analytical Plan → Query Graph → SQL',
  },
  {
    id: 'governance',
    number: '03',
    label: 'Governance & Security Layer',
    sublabel: "VoxCore's Core Differentiator",
    color: '#f97316',
    border: 'rgba(249,115,22,0.35)',
    bg: 'rgba(249,115,22,0.06)',
    icon: '🛡',
    description:
      "Most AI data tools skip this layer. VoxCore's governance engine sits between every AI-generated query and your database, enforcing policy, detecting risk, and logging every action.",
    modules: [
      'Policy Engine',
      'Risk Engine',
      'Query Inspector',
      'Sensitive Column Protection',
      'Approval Workflow',
      'Audit Logging',
    ],
    capabilities: [
      'Enforce governance rules',
      'Detect risky SQL (DROP, DELETE without WHERE)',
      'Protect PII / sensitive columns',
      'Block dangerous operations',
      'Track and audit all AI queries',
    ],
    flow: 'Generated SQL → Policy Engine → Risk Scoring → Simulation → Approved Execution',
    policyExamples: [
      'Block DROP TABLE',
      'Block DELETE without WHERE',
      'Mask SSN columns',
      'Require approval for large scans',
    ],
  },
  {
    id: 'execution',
    number: '04',
    label: 'Query Execution Layer',
    sublabel: 'Safe Database Interaction',
    color: '#34d399',
    border: 'rgba(52,211,153,0.35)',
    bg: 'rgba(52,211,153,0.06)',
    icon: '⚡',
    description:
      'Queries never touch production databases without passing through simulation and risk checks. The execution layer compiles, estimates cost, and formats results for the UI.',
    modules: [
      'Query Simulator',
      'Connection Manager',
      'Execution Engine',
      'Result Formatter',
    ],
    capabilities: [
      'Run EXPLAIN simulations',
      'Estimate query cost & row scans',
      'Execute queries safely',
      'Format results for charts',
    ],
    flow: 'SQL Query → Simulation (EXPLAIN) → Risk Check → Execution → Result Set',
  },
  {
    id: 'data',
    number: '05',
    label: 'Enterprise Data Sources',
    sublabel: 'Multi-Database Connectors',
    color: '#fbbf24',
    border: 'rgba(251,191,36,0.35)',
    bg: 'rgba(251,191,36,0.06)',
    icon: '🗄',
    description:
      'VoxCore connects to any enterprise database. Credentials are encrypted, workspace-scoped, and isolated per tenant.',
    modules: [
      'SQL Server Connector',
      'PostgreSQL Connector',
      'MySQL Connector',
      'Snowflake Connector',
      'BigQuery Connector',
    ],
    capabilities: [
      'Encrypted credential storage',
      'Workspace-scoped connections',
      'Tenant isolation',
      'Cross-database schema intelligence',
    ],
    flow: 'Database Connector → Connection Manager → Execution Engine',
  },
];

const OBSERVABILITY_METRICS = [
  { label: 'AI Queries Executed', icon: '📈' },
  { label: 'Risk Distribution', icon: '🔴' },
  { label: 'Blocked Queries', icon: '🚫' },
  { label: 'Policy Violations', icon: '⚠️' },
  { label: 'Top Data Sources', icon: '🗄' },
  { label: 'Query Performance', icon: '⚡' },
];

const E2E_FLOW = [
  { step: 'User Question', color: '#4f8cff', layer: 'UI' },
  { step: 'Intent Detection', color: '#a78bfa', layer: 'AI Brain' },
  { step: 'Semantic Brain', color: '#a78bfa', layer: 'AI Brain' },
  { step: 'Analytical Plan', color: '#a78bfa', layer: 'AI Brain' },
  { step: 'Query Graph', color: '#a78bfa', layer: 'AI Brain' },
  { step: 'SQL Generation', color: '#a78bfa', layer: 'AI Brain' },
  { step: 'Policy Engine', color: '#f97316', layer: 'Governance' },
  { step: 'Risk Engine', color: '#f97316', layer: 'Governance' },
  { step: 'Query Simulation', color: '#34d399', layer: 'Execution' },
  { step: 'Execution', color: '#34d399', layer: 'Execution' },
  { step: 'Chart + Insights', color: '#4f8cff', layer: 'UI' },
];

const INTERNAL_MODELS = [
  {
    title: 'Semantic Model',
    color: '#a78bfa',
    items: [
      'revenue = SUM(sales_amount)',
      'orders = COUNT(order_id)',
      'avg_order = AVG(order_total)',
    ],
    fields: ['metrics', 'dimensions', 'time dimensions', 'relationships'],
  },
  {
    title: 'Query Graph',
    color: '#4f8cff',
    items: [
      'metric → revenue',
      'dimension → district',
      'comparison → YoY',
      'chart → bar_chart',
    ],
    fields: ['nodes', 'compiled_sql', 'drilldowns', 'explanation'],
  },
  {
    title: 'Analytical Plan',
    color: '#34d399',
    items: [
      'analysis_type: comparison',
      'metric: revenue',
      'dimension: district',
      'time_grain: year',
    ],
    fields: ['analysis_type', 'metric', 'dimension', 'comparison', 'time_grain'],
  },
];

const PILLARS = [
  {
    id: 'semantic',
    badge: '1',
    title: 'Semantic Intelligence Layer',
    subtitle: 'The Business Context Engine',
    color: '#7c9cff',
    icon: '🧭',
    description:
      'VoxCore understands business metrics, dimension hierarchies, table relationships, time intelligence, and aggregation logic so the system reasons in business language, not raw SQL tokens.',
    bullets: [
      'Business metrics and semantic definitions',
      'Dimension hierarchies and table relationships',
      'Time intelligence and aggregation rules',
    ],
  },
  {
    id: 'brain',
    badge: '2',
    title: 'The VoxCore Brain',
    subtitle: 'AI-Native Analytics Intelligence',
    color: '#a78bfa',
    icon: '🧠',
    description:
      'The Brain interprets business intent, builds analytical plans, generates safe optimized SQL, and recommends visuals so VoxCore behaves like an analyst rather than a chatbot.',
    bullets: [
      'Interprets business questions into metrics and dimensions',
      'Builds analytical plans and Query Graphs',
      'Generates SQL and chart recommendations',
    ],
  },
  {
    id: 'guardian',
    badge: '3',
    title: 'Data Guardian AI',
    subtitle: 'AI Database Security Layer',
    color: '#fb923c',
    icon: '🛡',
    description:
      'Data Guardian AI validates every AI query, enforces policy, blocks sensitive exposure, and audits activity before anything reaches enterprise data systems.',
    bullets: [
      'Pre-execution query validation and risk checks',
      'Sensitive data controls and policy enforcement',
      'Auditability and governance observability',
    ],
  },
];

// ── Component ───────────────────────────────────────────────────────────────

export default function Architecture() {
  const [activeLayer, setActiveLayer] = useState<string | null>(null);

  return (
    <div style={{ color: '#e8f0ff', maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 8 }}>
        <img src="/assets/vc_logo.png" alt="VoxCore" style={{ width: 40, height: 40, objectFit: 'contain' }} />
        <PageHeader
          title="VoxCore v1.0 Architecture"
          subtitle="Enterprise AI Analytics + Governance Platform Blueprint"
        />
      </div>

      {/* Positioning badge */}
      <div style={{
        display: 'inline-flex',
        gap: 8,
        flexWrap: 'wrap',
        marginBottom: 28,
      }}>
        {['AI Analytics Platform', 'AI Database Governance', 'Enterprise-Grade', 'Deterministic Analytics'].map((tag) => (
          <span key={tag} style={{
            background: 'rgba(79,140,255,0.12)',
            color: '#a8c4f0',
            border: '1px solid rgba(79,140,255,0.28)',
            borderRadius: 999,
            padding: '4px 12px',
            fontSize: 12,
            fontWeight: 600,
          }}>{tag}</span>
        ))}
      </div>

      <section style={{ ...cardStyle, marginBottom: 24 }}>
        <h2 style={sectionTitle}>The 3 Pillars of VoxCore</h2>
        <p style={{ color: 'var(--platform-muted)', fontSize: 13, marginBottom: 18 }}>
          VoxCore is an AI-secure analytics platform where the VoxCore Brain generates insights while Data Guardian AI governs database access.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
          {PILLARS.map((pillar) => (
            <div
              key={pillar.id}
              style={{
                borderRadius: 12,
                border: `1px solid ${pillar.color}45`,
                background: `${pillar.color}10`,
                padding: '16px 16px 14px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <span
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: 999,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 11,
                    fontWeight: 800,
                    color: '#0f172a',
                    background: pillar.color,
                  }}
                >
                  {pillar.badge}
                </span>
                <span style={{ fontSize: 18 }}>{pillar.icon}</span>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#e8f0ff' }}>{pillar.title}</div>
              </div>

              <div style={{ fontSize: 12, color: pillar.color, fontWeight: 700, marginBottom: 8 }}>
                {pillar.subtitle}
              </div>

              <p style={{ margin: '0 0 10px', fontSize: 12, color: '#c7d2fe', lineHeight: 1.55 }}>
                {pillar.description}
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {pillar.bullets.map((line) => (
                  <div key={line} style={{ fontSize: 12, color: '#dbe7ff' }}>• {line}</div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 16,
            borderRadius: 10,
            border: '1px solid rgba(79,140,255,0.25)',
            background: 'rgba(10,20,36,0.55)',
            padding: '10px 12px',
            fontSize: 12,
            color: '#a8c4f0',
            fontFamily: 'monospace',
          }}
        >
          User → Semantic Intelligence → VoxCore Brain → Data Guardian AI → Enterprise Databases
        </div>
      </section>

      {/* ── Five-Layer Stack ──────────────────────────────────────────── */}
      <section style={cardStyle}>
        <h2 style={sectionTitle}>Five-Layer Architecture</h2>
        <p style={{ color: 'var(--platform-muted)', marginBottom: 24, fontSize: 13 }}>
          Click any layer to expand details.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {LAYERS.map((layer, idx) => {
            const isOpen = activeLayer === layer.id;
            return (
              <div key={layer.id}>
                {/* Layer header */}
                <button
                  onClick={() => setActiveLayer(isOpen ? null : layer.id)}
                  style={{
                    width: '100%',
                    display: 'grid',
                    gridTemplateColumns: '56px 1fr auto',
                    alignItems: 'center',
                    gap: 16,
                    padding: '14px 18px',
                    background: isOpen ? layer.bg : 'transparent',
                    border: `1px solid ${isOpen ? layer.border : 'var(--platform-border)'}`,
                    borderRadius: 10,
                    cursor: 'pointer',
                    textAlign: 'left',
                    color: '#e8f0ff',
                    transition: 'all 0.15s',
                  }}
                >
                  <div style={{
                    width: 42,
                    height: 42,
                    borderRadius: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `${layer.color}22`,
                    border: `1px solid ${layer.border}`,
                    fontSize: 20,
                  }}>
                    {layer.icon}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 15 }}>
                      <span style={{ color: layer.color, marginRight: 8, fontSize: 11, fontWeight: 800, letterSpacing: 1 }}>
                        LAYER {layer.number}
                      </span>
                      {layer.label}
                    </div>
                    <div style={{ color: 'var(--platform-muted)', fontSize: 12, marginTop: 2 }}>{layer.sublabel}</div>
                  </div>
                  <div style={{ color: isOpen ? layer.color : 'var(--platform-muted)', fontSize: 18 }}>
                    {isOpen ? '▲' : '▼'}
                  </div>
                </button>

                {/* Expanded detail */}
                {isOpen && (
                  <div style={{
                    padding: '20px 20px 20px 76px',
                    border: `1px solid ${layer.border}`,
                    borderTop: 'none',
                    borderRadius: '0 0 10px 10px',
                    background: layer.bg,
                    marginBottom: 4,
                  }}>
                    <p style={{ color: '#c8deff', fontSize: 13, marginTop: 0, marginBottom: 16 }}>{layer.description}</p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 16 }}>
                      <div>
                        <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: layer.color, marginBottom: 8 }}>Core Modules</div>
                        {layer.modules.map((m) => (
                          <div key={m} style={{ fontSize: 13, color: '#dbe7ff', padding: '3px 0' }}>· {m}</div>
                        ))}
                      </div>
                      <div>
                        <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: layer.color, marginBottom: 8 }}>Responsibilities</div>
                        {layer.capabilities.map((c) => (
                          <div key={c} style={{ fontSize: 13, color: '#dbe7ff', padding: '3px 0' }}>✓ {c}</div>
                        ))}
                      </div>
                      {'policyExamples' in layer && Array.isArray(layer.policyExamples) && (
                        <div>
                          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: layer.color, marginBottom: 8 }}>Example Policy Rules</div>
                          {layer.policyExamples.map((p) => (
                            <div key={p} style={{ fontSize: 13, color: '#ffd6b3', padding: '3px 0' }}>⚠ {p}</div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div style={{
                      padding: '10px 14px',
                      background: 'rgba(0,0,0,0.25)',
                      borderRadius: 8,
                      fontSize: 12,
                      fontFamily: 'monospace',
                      color: '#a8c4f0',
                      borderLeft: `3px solid ${layer.color}`,
                    }}>
                      {layer.flow}
                    </div>
                  </div>
                )}

                {/* Arrow between layers */}
                {idx < LAYERS.length - 1 && (
                  <div style={{ textAlign: 'center', color: 'var(--platform-muted)', fontSize: 20, lineHeight: '28px' }}>↓</div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ── End-to-End Flow ───────────────────────────────────────────── */}
      <section style={{ ...cardStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>End-to-End Query Flow</h2>
        <p style={{ color: 'var(--platform-muted)', fontSize: 13, marginBottom: 20 }}>
          Every user question travels through this deterministic pipeline before a single row is returned.
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 0, alignItems: 'center' }}>
          {E2E_FLOW.map((item, idx) => (
            <React.Fragment key={item.step}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 4,
                minWidth: 88,
              }}>
                <div style={{
                  padding: '8px 12px',
                  borderRadius: 8,
                  background: `${item.color}14`,
                  border: `1px solid ${item.color}55`,
                  color: item.color,
                  fontSize: 12,
                  fontWeight: 700,
                  textAlign: 'center',
                  whiteSpace: 'nowrap',
                }}>
                  {item.step}
                </div>
                <div style={{ fontSize: 10, color: 'var(--platform-muted)', fontWeight: 600 }}>{item.layer}</div>
              </div>
              {idx < E2E_FLOW.length - 1 && (
                <div style={{ color: 'var(--platform-muted)', fontSize: 16, padding: '0 2px', marginBottom: 14 }}>→</div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* ── Internal Data Models ──────────────────────────────────────── */}
      <section style={{ ...cardStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>Core Internal Data Models</h2>
        <p style={{ color: 'var(--platform-muted)', fontSize: 13, marginBottom: 20 }}>
          Three structured models are the backbone of every analytical operation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {INTERNAL_MODELS.map((model) => (
            <div key={model.title} style={{
              padding: 18,
              borderRadius: 12,
              border: `1px solid ${model.color}40`,
              background: `${model.color}0a`,
            }}>
              <div style={{ fontWeight: 700, fontSize: 15, color: model.color, marginBottom: 10 }}>{model.title}</div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--platform-muted)', marginBottom: 6 }}>Fields</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 12 }}>
                {model.fields.map((f) => (
                  <span key={f} style={{
                    background: `${model.color}18`,
                    border: `1px solid ${model.color}30`,
                    borderRadius: 6,
                    padding: '2px 8px',
                    fontSize: 11,
                    color: '#dbe7ff',
                  }}>{f}</span>
                ))}
              </div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--platform-muted)', marginBottom: 6 }}>Example</div>
              {model.items.map((item) => (
                <div key={item} style={{ fontFamily: 'monospace', fontSize: 12, color: '#a8c4f0', padding: '2px 0' }}>{item}</div>
              ))}
            </div>
          ))}
        </div>
      </section>

      {/* ── Observability Layer ───────────────────────────────────────── */}
      <section style={{ ...cardStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>Observability Layer</h2>
        <p style={{ color: 'var(--platform-muted)', fontSize: 13, marginBottom: 20 }}>
          Enterprise systems need monitoring. VoxCore surfaces platform health through the Governance Dashboard.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
          {OBSERVABILITY_METRICS.map((metric) => (
            <div key={metric.label} style={{
              padding: '16px 14px',
              borderRadius: 10,
              border: '1px solid var(--platform-border)',
              background: 'rgba(79,140,255,0.05)',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>{metric.icon}</div>
              <div style={{ fontSize: 12, color: '#c8deff', fontWeight: 600 }}>{metric.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Deployment Architecture ───────────────────────────────────── */}
      <section style={{ ...cardStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>Deployment Architecture</h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Current */}
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#34d399', marginBottom: 12 }}>Current — Render</div>
            {['FastAPI Backend', 'React Frontend', 'SQLite / SQL Server', 'Uvicorn ASGI'].map((item) => (
              <div key={item} style={deployNode('#34d399')}>{item}</div>
            ))}
          </div>

          {/* Future */}
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#a78bfa', marginBottom: 12 }}>Future — Scalable</div>
            {[
              'Load Balancer',
              'API Servers (FastAPI)',
              'Semantic Brain Service',
              'Governance Engine',
              'Execution Workers',
              'Enterprise Databases',
            ].map((item) => (
              <div key={item} style={deployNode('#a78bfa')}>{item}</div>
            ))}
            <div style={{ marginTop: 10, fontSize: 11, color: 'var(--platform-muted)' }}>
              Optional: Redis (cache) · Vector DB (semantic search) · Kafka (query events)
            </div>
          </div>
        </div>
      </section>

      {/* ── Market Positioning ────────────────────────────────────────── */}
      <section style={{ ...cardStyle, marginTop: 24, background: 'rgba(7,17,31,0.85)', border: '1px solid rgba(79,140,255,0.2)' }}>
        <h2 style={sectionTitle}>Market Positioning</h2>
        <p style={{ color: '#a8c4f0', fontSize: 13, marginBottom: 20 }}>
          The combination of AI-native analytics and database governance is rare. VoxCore occupies a unique and defensible category.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 24 }}>
          {[
            { name: 'Snowflake Cortex', strength: 'AI data cloud' },
            { name: 'Databricks AI', strength: 'AI data lake' },
            { name: 'ThoughtSpot Sage', strength: 'AI BI' },
            { name: 'VoxCore', strength: 'AI Analytics + AI Governance', highlight: true },
          ].map((row) => (
            <div key={row.name} style={{
              padding: '14px 16px',
              borderRadius: 10,
              border: row.highlight ? '1px solid rgba(79,140,255,0.5)' : '1px solid var(--platform-border)',
              background: row.highlight ? 'rgba(79,140,255,0.12)' : 'rgba(255,255,255,0.03)',
            }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: row.highlight ? '#7dd3fc' : '#dbe7ff', marginBottom: 4 }}>{row.name}</div>
              <div style={{ fontSize: 12, color: 'var(--platform-muted)' }}>{row.strength}</div>
              {row.highlight && <div style={{ marginTop: 6, fontSize: 11, color: '#4f8cff', fontWeight: 700 }}>← VoxCore</div>}
            </div>
          ))}
        </div>

        <div style={{
          padding: '16px 20px',
          borderRadius: 12,
          background: 'rgba(79,140,255,0.08)',
          border: '1px solid rgba(79,140,255,0.2)',
          borderLeft: '4px solid #4f8cff',
        }}>
          <div style={{ fontSize: 13, color: '#c8deff', fontWeight: 600, marginBottom: 6 }}>Strategic Positioning</div>
          <div style={{ fontSize: 14, color: '#dbe7ff', lineHeight: 1.7 }}>
            <strong style={{ color: '#7dd3fc' }}>AI → VoxCore Governance Layer → Enterprise Data</strong>
          </div>
          <div style={{ fontSize: 13, color: 'var(--platform-muted)', marginTop: 8 }}>
            VoxCore is not just an AI SQL interface — it is a{' '}
            <strong style={{ color: '#a8c4f0' }}>secure AI analytics operating system for databases.</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

// ── Style helpers ─────────────────────────────────────────────────────────

const cardStyle: React.CSSProperties = {
  background: 'var(--platform-card-bg)',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 24,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 6,
  fontSize: '1.1rem',
  color: '#e8f0ff',
};

function deployNode(color: string): React.CSSProperties {
  return {
    padding: '8px 14px',
    borderRadius: 8,
    marginBottom: 4,
    fontSize: 13,
    color: '#dbe7ff',
    background: `${color}0c`,
    border: `1px solid ${color}30`,
  };
}
