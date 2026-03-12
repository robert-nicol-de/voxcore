import React, { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import './App.css';
import { Login } from './screens/Login';
import { UserDropdown } from './components/UserDropdown';
import Dashboard from './pages/Dashboard';
import Databases from './pages/Databases';
import Policies from './pages/Policies';
import QueryLogs from './pages/QueryLogs';
import Sandbox from './pages/Sandbox';
import SqlAssistant from './pages/SqlAssistant';
import { Sidebar } from './components/Sidebar';
import SettingsPage from './pages/Settings';
import { useWorkspace } from './context/WorkspaceContext';

const platformFeatures = [
  {
    title: 'Dashboard',
    description: 'Monitor AI activity across connected databases.',
  },
  {
    title: 'Database Manager',
    description: 'Securely connect and manage multiple databases.',
  },
  {
    title: 'SQL Assistant',
    description: 'Generate and validate SQL with AI safely.',
  },
  {
    title: 'Query Activity Monitor',
    description: 'Track every AI-generated query in real time.',
  },
  {
    title: 'AI Query Sandbox',
    description: 'Preview query results before running them in production.',
  },
  {
    title: 'Policy Engine',
    description: 'Define rules that control how AI interacts with data.',
  },
  {
    title: 'Schema Intelligence',
    description: 'Automatically understand tables, columns, and relationships.',
  },
];

const governancePoints = [
  'query inspection',
  'AI risk scoring',
  'sandbox execution',
  'policy enforcement',
  'query activity logs',
  'sensitive data detection',
];

const audiences = [
  'Data teams adopting AI tools',
  'Security teams enforcing data governance',
  'Organizations protecting production databases',
  'Developers building AI data applications',
];

const riskList = [
  'destructive queries',
  'sensitive data exposure',
  'unauthorized access',
  'compliance violations',
];

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginPage, setShowLoginPage] = useState(false);
  const navigate = useNavigate();
  const { currentWorkspace } = useWorkspace();

  useEffect(() => {
    const token = localStorage.getItem('voxcore_token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
    navigate('/app/dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem('token');
    localStorage.removeItem('voxcore_token');
    localStorage.removeItem('voxcore_user_name');
    localStorage.removeItem('voxcore_user_email');
    localStorage.removeItem('voxcore_org_id');
    localStorage.removeItem('voxcore_org_name');
    localStorage.removeItem('voxcore_company_id');
    localStorage.removeItem('voxcore_workspace_id');
    localStorage.removeItem('voxcore_workspace_name');
    navigate('/');
  };

  const scrollToDemo = () => {
    document.getElementById('voxcore-demo')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  if (!isLoggedIn) {
    if (showLoginPage) {
      return <Login onLogin={handleLogin} />;
    }
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #07111f 0%, #0b1830 45%, #f2f5f9 45.1%, #f2f5f9 100%)' }}>
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '18px 28px',
            position: 'sticky',
            top: 0,
            zIndex: 20,
            backdropFilter: 'blur(14px)',
            background: 'rgba(7,17,31,0.78)',
            borderBottom: '1px solid rgba(148,163,184,0.14)',
          }}
        >
          <div style={{ color: '#f8fafc', fontWeight: 800, fontSize: '1.3rem', letterSpacing: '-0.04em' }}>
            VoxCloud
            <div style={{ color: '#7dd3fc', fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: 2 }}>
              Powered by the VoxCore Engine
            </div>
          </div>
          <nav style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button
              style={{ background: 'transparent', color: '#cbd5e1', border: '1px solid rgba(148,163,184,0.35)', borderRadius: '999px', padding: '10px 16px', fontWeight: 700, cursor: 'pointer' }}
              onClick={scrollToDemo}
            >
              View Demo
            </button>
            <button
              style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)', color: '#fff', border: 'none', borderRadius: '999px', padding: '10px 18px', fontWeight: 800, cursor: 'pointer', boxShadow: '0 10px 30px rgba(14,165,233,0.35)' }}
              onClick={() => setShowLoginPage(true)}
            >
              Launch VoxCloud
            </button>
          </nav>
        </header>

        <main>
          <section
            style={{
              color: '#fff',
              padding: '72px 28px 120px',
              maxWidth: 1280,
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1.15fr) minmax(320px, 0.85fr)',
              gap: 28,
              alignItems: 'center',
            }}
          >
            <div>
              <img src="/assets/VC_full_logo_text.png" alt="VoxCore" style={{ width: 420, maxWidth: '100%', marginBottom: 20 }} />
              <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#a6d3ff', marginTop: 0 }}>AI Data Governance Platform</p>
              <p style={{ marginTop: 8, maxWidth: 700, fontSize: '1.2rem', lineHeight: 1.6, color: '#cbd5e1' }}>
                Control How AI Touches Your Data
              </p>
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 28 }}>
                <button
                  style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)', color: '#fff', border: 'none', borderRadius: '999px', padding: '14px 22px', fontWeight: 800, cursor: 'pointer', boxShadow: '0 12px 34px rgba(14,165,233,0.34)' }}
                  onClick={() => setShowLoginPage(true)}
                >
                  Launch VoxCloud
                </button>
                <button
                  style={{ background: 'rgba(15,23,42,0.35)', color: '#e2e8f0', border: '1px solid rgba(148,163,184,0.3)', borderRadius: '999px', padding: '14px 22px', fontWeight: 800, cursor: 'pointer' }}
                  onClick={scrollToDemo}
                >
                  View Demo
                </button>
              </div>
            </div>

            <div
              id="voxcore-demo"
              style={{
                background: 'linear-gradient(180deg, rgba(15,23,42,0.96) 0%, rgba(8,15,30,0.98) 100%)',
                borderRadius: 28,
                border: '1px solid rgba(96,165,250,0.18)',
                padding: 24,
                boxShadow: '0 30px 70px rgba(2,6,23,0.55)',
              }}
            >
              <div style={{ color: '#7dd3fc', fontSize: '0.85rem', fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                AI Query Security Pipeline
              </div>
              <div style={{ marginTop: 16, display: 'grid', gap: 10 }}>
                {['User Prompt', 'AI generates SQL', 'VoxCore Query Inspector', 'AI Risk Engine', 'Policy Engine', 'Sandbox Execution', 'Production Database'].map((step, index) => (
                  <div key={step} style={{ display: 'grid', gridTemplateColumns: '42px 1fr', gap: 12, alignItems: 'center' }}>
                    <div style={{ width: 42, height: 42, borderRadius: 999, background: index < 5 ? 'rgba(14,165,233,0.16)' : 'rgba(34,197,94,0.16)', border: '1px solid rgba(125,211,252,0.22)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#e0f2fe', fontWeight: 800 }}>
                      {index + 1}
                    </div>
                    <div style={{ padding: '12px 14px', borderRadius: 16, background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(148,163,184,0.12)', color: '#f8fafc' }}>
                      {step}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section style={{ background: '#f2f5f9', color: '#0f172a', padding: '44px 28px 24px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gap: 22 }}>
              <div>
                <div style={{ color: '#dc2626', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Problem</div>
                <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3.4rem)', letterSpacing: '-0.05em', marginTop: 10 }}>AI + Databases Without Guardrails Is Dangerous</h2>
                <p style={{ marginTop: 14, maxWidth: 900, color: '#334155', fontSize: '1.05rem', lineHeight: 1.7 }}>
                  AI tools can generate powerful SQL queries in seconds. But connecting AI directly to production databases creates serious risks.
                </p>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
                {riskList.map((item) => (
                  <div key={item} style={{ padding: 18, borderRadius: 18, background: '#fff', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 8px 24px rgba(15,23,42,0.05)' }}>
                    <div style={{ color: '#dc2626', fontWeight: 800, marginBottom: 8 }}>•</div>
                    <div style={{ fontWeight: 700 }}>{item}</div>
                  </div>
                ))}
              </div>
              <p style={{ color: '#475569', fontSize: '1rem', lineHeight: 1.7 }}>
                Most AI tools were never designed to safely interact with enterprise databases.
              </p>
            </div>
          </section>

          <section style={{ background: '#f2f5f9', color: '#0f172a', padding: '48px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gap: 24 }}>
              <div>
                <div style={{ color: '#0284c7', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Solution</div>
                <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3.1rem)', letterSpacing: '-0.05em', marginTop: 10 }}>Meet VoxCore</h2>
                <p style={{ marginTop: 14, maxWidth: 860, color: '#334155', fontSize: '1.05rem', lineHeight: 1.7 }}>
                  VoxCore acts as a governance layer between AI and your database. Every AI-generated query is analyzed before execution.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 18, alignItems: 'center' }}>
                <div style={{ background: '#0f172a', color: '#f8fafc', borderRadius: 18, padding: 22, textAlign: 'center', fontWeight: 800 }}>AI Tool</div>
                <div style={{ fontSize: '1.8rem', color: '#0ea5e9', fontWeight: 900 }}>↓</div>
                <div style={{ background: 'linear-gradient(135deg, #e0f2fe 0%, #bfdbfe 100%)', borderRadius: 18, padding: 22, textAlign: 'center', fontWeight: 900 }}>VoxCore Governance Layer</div>
                <div></div>
                <div style={{ fontSize: '1.8rem', color: '#0ea5e9', fontWeight: 900 }}>↓</div>
                <div style={{ background: '#0f172a', color: '#f8fafc', borderRadius: 18, padding: 22, textAlign: 'center', fontWeight: 800 }}>Your Database</div>
              </div>

              <p style={{ color: '#334155', fontSize: '1.05rem', lineHeight: 1.7 }}>
                This ensures every query is safe, auditable, and policy-compliant.
              </p>
            </div>
          </section>

          <section style={{ background: '#eaf1f8', color: '#0f172a', padding: '52px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(320px, 420px)', gap: 28 }}>
              <div>
                <div style={{ color: '#0f766e', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>How VoxCore Works</div>
                <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', letterSpacing: '-0.05em', marginTop: 10 }}>AI Query Security Pipeline</h2>
                <div style={{ marginTop: 20, display: 'grid', gap: 10 }}>
                  {['User Prompt', 'AI generates SQL', 'VoxCore Query Inspector', 'AI Risk Engine', 'Policy Engine', 'Sandbox Execution', 'Production Database'].map((step) => (
                    <div key={step} style={{ padding: '14px 18px', borderRadius: 14, background: '#fff', border: '1px solid rgba(15,23,42,0.08)', fontWeight: 700 }}>
                      {step}
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ background: '#0f172a', color: '#e2e8f0', borderRadius: 24, padding: 24, alignSelf: 'start' }}>
                <div style={{ color: '#7dd3fc', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '0.8rem' }}>Before a query ever touches your database</div>
                <div style={{ display: 'grid', gap: 12, marginTop: 18 }}>
                  {['inspects SQL structure', 'analyzes risk level', 'enforces security policies', 'logs activity for auditing'].map((item) => (
                    <div key={item} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <span style={{ color: '#22c55e', fontWeight: 900 }}>✔</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section style={{ background: '#f8fafc', color: '#0f172a', padding: '56px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto' }}>
              <div style={{ color: '#2563eb', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Platform Features</div>
              <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', letterSpacing: '-0.05em', marginTop: 10 }}>VoxCloud Platform</h2>
              <p style={{ color: '#475569', marginTop: 12, fontSize: '1rem' }}>Powered by the VoxCore Engine</p>

              <div style={{ marginTop: 24, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
                {platformFeatures.map((feature) => (
                  <div key={feature.title} style={{ background: '#fff', borderRadius: 18, padding: 20, border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 10px 28px rgba(15,23,42,0.05)' }}>
                    <h3 style={{ fontSize: '1.05rem', marginBottom: 10 }}>{feature.title}</h3>
                    <p style={{ color: '#475569', lineHeight: 1.6 }}>{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section style={{ background: '#0f172a', color: '#f8fafc', padding: '58px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(300px, 0.9fr)', gap: 28 }}>
              <div>
                <div style={{ color: '#7dd3fc', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Security & Governance</div>
                <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', letterSpacing: '-0.05em', marginTop: 10 }}>Built for Secure AI Adoption</h2>
                <p style={{ color: '#cbd5e1', lineHeight: 1.8, marginTop: 14, maxWidth: 760 }}>
                  VoxCore gives organizations complete visibility and control over AI database access. Every query becomes auditable and governed.
                </p>
              </div>
              <div style={{ display: 'grid', gap: 12 }}>
                {governancePoints.map((item) => (
                  <div key={item} style={{ padding: '14px 16px', borderRadius: 14, background: 'rgba(15,23,42,0.5)', border: '1px solid rgba(148,163,184,0.16)', color: '#e2e8f0' }}>
                    • {item}
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section style={{ background: '#f2f5f9', color: '#0f172a', padding: '54px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto' }}>
              <div style={{ color: '#0f766e', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Who VoxCore Is For</div>
              <div style={{ marginTop: 18, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
                {audiences.map((item) => (
                  <div key={item} style={{ background: '#fff', borderRadius: 18, padding: 18, border: '1px solid rgba(15,23,42,0.08)' }}>
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section style={{ background: 'linear-gradient(135deg, #082032 0%, #0f3d64 100%)', color: '#fff', padding: '64px 28px' }}>
            <div style={{ maxWidth: 960, margin: '0 auto', textAlign: 'center' }}>
              <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3.4rem)', letterSpacing: '-0.05em' }}>Secure your AI-generated database queries.</h2>
              <p style={{ marginTop: 16, color: '#dbeafe', fontSize: '1.1rem' }}>Start using VoxCloud today.</p>
              <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginTop: 28 }}>
                <button
                  style={{ background: '#fff', color: '#0f172a', border: 'none', borderRadius: '999px', padding: '14px 22px', fontWeight: 800, cursor: 'pointer' }}
                  onClick={() => setShowLoginPage(true)}
                >
                  Launch VoxCloud
                </button>
              </div>
            </div>
          </section>
        </main>

        <footer style={{ background: '#07111f', color: '#cbd5e1', padding: '28px 28px 40px' }}>
          <div style={{ maxWidth: 1160, margin: '0 auto' }}>
            <div style={{ fontWeight: 800, color: '#f8fafc' }}>VoxCloud</div>
            <div style={{ marginTop: 6 }}>Powered by the VoxCore Engine</div>
            <div style={{ marginTop: 14, color: '#7dd3fc', fontWeight: 700 }}>AI Database Governance Platform</div>
          </div>
        </footer>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--platform-bg)' }}>
      <header
        style={{
          height: 72,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          borderBottom: '1px solid var(--platform-border)',
          background: 'var(--platform-topbar-bg)',
          position: 'sticky',
          top: 0,
          zIndex: 30,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <img src="/assets/vc_logo.png" alt="VoxCloud" style={{ width: 28, height: 28, objectFit: 'contain' }} />
          <div>
            <div style={{ color: '#ffffff', fontSize: 24, fontWeight: 700, letterSpacing: '-0.03em' }}>VoxCloud</div>
            <div style={{ color: 'var(--platform-muted)', fontSize: 12, marginTop: 2 }}>AI Data Governance Platform</div>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '8px 14px',
            borderRadius: 999,
            border: '1px solid var(--platform-border)',
            background: 'rgba(79,140,255,0.08)',
            color: 'var(--platform-muted)',
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          Workspace:
          <span style={{ color: '#ffffff', fontWeight: 700 }}>{currentWorkspace?.name || 'Default'}</span>
        </div>

        <UserDropdown token={localStorage.getItem('voxcore_token') || ''} onLogout={handleLogout} />
      </header>

      <div style={{ display: 'flex', minHeight: 'calc(100vh - 72px)' }}>
        <Sidebar />
        <main style={{ flex: 1, minWidth: 0, padding: 24 }}>
          <Routes>
            <Route path="/app/dashboard" element={<Dashboard />} />
            <Route path="/app/databases" element={<Databases />} />
            <Route path="/app/policies" element={<Policies />} />
            <Route path="/app/query-logs" element={<QueryLogs />} />
            <Route path="/app/sandbox" element={<Sandbox />} />
            <Route path="/app/settings" element={<SettingsPage />} />
            <Route path="/app" element={<SqlAssistant />} />
            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
