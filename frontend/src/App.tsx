import React, { Suspense, lazy, useEffect, useState } from 'react';
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import './App.css';
import { Login } from './screens/Login';
import { UserDropdown } from './components/UserDropdown';
import Dashboard from './pages/Dashboard';
import Databases from './pages/Databases';
import DataSourcesPage from './pages/DataSources';
import DataSourceNewPage from './pages/DataSourceNew';
import SemanticModelsPage from './pages/SemanticModels';
import Policies from './pages/Policies';
import QueryLogs from './pages/QueryLogs';
import QueryInvestigation from './pages/QueryInvestigation';
import Sandbox from './pages/Sandbox';
import SqlAssistant from './pages/SqlAssistant';
import { Sidebar } from './components/Sidebar';
import SettingsPage from './pages/Settings';
import SchemaExplorerPage from './pages/SchemaExplorerPage';
import ArchitecturePage from './pages/Architecture';
import AgentInsightsPage from './pages/AgentInsights';
import RequireAuth from './components/auth/RequireAuth';
import WorkspaceSwitcher from './components/WorkspaceSwitcher';
import { apiUrl } from './lib/api';

const ControlCenter = lazy(() => import('./pages/ControlCenter'));

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
  const [launchingPlayground, setLaunchingPlayground] = useState(false);
  const [playgroundError, setPlaygroundError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token');

  useEffect(() => {
    const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
    const redirectTarget = localStorage.getItem('voxcore_post_login_redirect') || '/app/dashboard';
    localStorage.removeItem('voxcore_post_login_redirect');
    navigate(redirectTarget);
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
    localStorage.removeItem('voxcore_role');
    localStorage.removeItem('voxcore_is_super_admin');
    navigate('/');
  };

  const navigateToPlatform = (path: string) => {
    if (token) {
      navigate(path);
      return;
    }
    localStorage.setItem('voxcore_post_login_redirect', path);
    setShowLoginPage(true);
  };

  const scrollToSection = (sectionId: string) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const launchPlayground = async () => {
    setLaunchingPlayground(true);
    setPlaygroundError('');
    try {
      const healthAbort = new AbortController();
      const healthTimer = window.setTimeout(() => healthAbort.abort(), 3500);
      let healthResponse: Response;
      try {
        healthResponse = await fetch(apiUrl('/api/v1/health'), {
          method: 'GET',
          signal: healthAbort.signal,
        });
      } finally {
        window.clearTimeout(healthTimer);
      }

      if (!healthResponse.ok) {
        setPlaygroundError('VoxCore backend is not healthy right now. Please make sure localhost:8000 is running.');
        return;
      }

      const response = await fetch(apiUrl('/api/v1/auth/playground'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expires_hours: 24 }),
      });
      if (!response.ok) {
        throw new Error('Unable to start playground session');
      }

      const data = await response.json();
      localStorage.setItem('voxcore_token', data.access_token);
      if (data.user_name) localStorage.setItem('voxcore_user_name', data.user_name);
      if (data.user_email) localStorage.setItem('voxcore_user_email', data.user_email);
      if (data.org_id != null) localStorage.setItem('voxcore_org_id', String(data.org_id));
      if (data.org_name) localStorage.setItem('voxcore_org_name', String(data.org_name));
      if (data.workspace_id != null) localStorage.setItem('voxcore_workspace_id', String(data.workspace_id));
      if (data.workspace_name) localStorage.setItem('voxcore_workspace_name', String(data.workspace_name));
      if (data.company_id != null) localStorage.setItem('voxcore_company_id', String(data.company_id));
      localStorage.setItem('voxcore_role', String(data.role || 'sandbox_user'));
      localStorage.setItem('voxcore_is_super_admin', 'false');

      setIsLoggedIn(true);
      const redirectTarget = localStorage.getItem('voxcore_post_login_redirect') || '/app/sandbox';
      localStorage.removeItem('voxcore_post_login_redirect');
      navigate(redirectTarget, { replace: true });
    } catch {
      setPlaygroundError('Backend is unreachable. Start VoxCore API on localhost:8000, then try Playground again.');
    } finally {
      setLaunchingPlayground(false);
    }
  };

  const protectedPaths = ['/dashboard', '/datasources', '/sql', '/schema', '/governance', '/workspaces'];
  const showAuthRequiredBanner = !token && new URLSearchParams(location.search).get('auth') === 'required';
  const isProtectedPath =
    location.pathname.startsWith('/app') ||
    location.pathname.startsWith('/datasources/new') ||
    protectedPaths.some((p) => location.pathname === p || location.pathname.startsWith(`${p}/`));

  if (!token && location.pathname === '/login') {
    return <Login onLogin={handleLogin} />;
  }

  if (token && location.pathname === '/login') {
    return <Navigate to="/app/dashboard" replace />;
  }

  if (!token && isProtectedPath) {
    return <Navigate to="/?auth=required" replace />;
  }

  if (!token) {
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
          <nav style={{ display: 'flex', gap: 8, alignItems: 'center', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
            {[
              { label: 'Platform', onClick: () => scrollToSection('platform-section') },
              { label: 'Features', onClick: () => scrollToSection('features-section') },
              { label: 'Pricing', onClick: () => scrollToSection('pricing-section') },
              { label: 'About', onClick: () => scrollToSection('about-section') },
            ].map((item) => (
              <button
                key={item.label}
                style={{
                  background: 'transparent',
                  color: '#bfdbfe',
                  border: 'none',
                  borderRadius: 999,
                  padding: '8px 10px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontSize: 14,
                }}
                onClick={item.onClick}
              >
                {item.label}
              </button>
            ))}
            <button
              style={{
                background: 'transparent',
                color: '#e2e8f0',
                border: '1px solid rgba(148,163,184,0.35)',
                borderRadius: 999,
                padding: '8px 14px',
                fontWeight: 700,
                cursor: 'pointer',
                fontSize: 14,
              }}
              onClick={() => setShowLoginPage(true)}
            >
              Login
            </button>
            <button
              style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)', color: '#fff', border: 'none', borderRadius: '999px', padding: '10px 18px', fontWeight: 800, cursor: 'pointer', boxShadow: '0 10px 30px rgba(14,165,233,0.35)' }}
              onClick={() => navigateToPlatform('/app/dashboard')}
            >
              Launch VoxCloud Platform
            </button>
          </nav>
        </header>

        <main>
          {showAuthRequiredBanner && (
            <div
              style={{
                margin: '14px auto 0',
                maxWidth: 1160,
                borderRadius: 10,
                padding: '10px 14px',
                border: '1px solid rgba(251,191,36,0.35)',
                color: '#fef3c7',
                background: 'rgba(120,53,15,0.35)',
                fontSize: 13,
              }}
            >
              You’re not signed in. Please log in to access VoxCore workspace routes.
            </div>
          )}
          <section
            id="platform-section"
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
              <div
                style={{
                  display: 'inline-flex',
                  padding: 10,
                  borderRadius: 14,
                  background: 'rgba(248,250,252,0.92)',
                  boxShadow: '0 16px 40px rgba(2,6,23,0.35)',
                  marginBottom: 20,
                }}
              >
                <img src="/assets/VC_full_logo_text.png" alt="VoxCore" style={{ width: 520, maxWidth: '100%', objectFit: 'contain' }} />
              </div>
              <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#a6d3ff', marginTop: 0 }}>AI Data Governance Platform</p>
              <p style={{ marginTop: 8, maxWidth: 700, fontSize: '1.2rem', lineHeight: 1.6, color: '#cbd5e1' }}>
                Control How AI Touches Your Data
              </p>
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 28 }}>
                <button
                  style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)', color: '#fff', border: 'none', borderRadius: '999px', padding: '14px 22px', fontWeight: 800, cursor: 'pointer', boxShadow: '0 12px 34px rgba(14,165,233,0.34)' }}
                  onClick={() => navigateToPlatform('/app/dashboard')}
                >
                  Launch VoxCloud Platform
                </button>
                <button
                  style={{ background: 'rgba(15,23,42,0.35)', color: '#e2e8f0', border: '1px solid rgba(148,163,184,0.3)', borderRadius: '999px', padding: '14px 22px', fontWeight: 800, cursor: 'pointer' }}
                  onClick={launchPlayground}
                >
                  {launchingPlayground ? 'Starting VoxCore Playground...' : 'Try VoxCore Playground'}
                </button>
              </div>
              {playgroundError ? (
                <div style={{ marginTop: 12, color: '#fca5a5', fontSize: 13, maxWidth: 620 }}>
                  {playgroundError}
                </div>
              ) : null}
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

          <section id="about-section" style={{ background: '#f2f5f9', color: '#0f172a', padding: '48px 28px' }}>
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

          <section id="features-section" style={{ background: '#f8fafc', color: '#0f172a', padding: '56px 28px' }}>
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

          <section id="pricing-section" style={{ background: '#eef4fb', color: '#0f172a', padding: '56px 28px' }}>
            <div style={{ maxWidth: 1160, margin: '0 auto' }}>
              <div style={{ color: '#0369a1', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.78rem' }}>Pricing</div>
              <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', letterSpacing: '-0.05em', marginTop: 10 }}>Enterprise-ready plans for every team</h2>
              <div style={{ marginTop: 24, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
                {[
                  { title: 'Starter', price: 'Free', note: 'Sandbox exploration and demo datasets.' },
                  { title: 'Growth', price: '$199 / mo', note: 'Production connectors, governance policies, and query monitoring.' },
                  { title: 'Enterprise', price: 'Custom', note: 'Private deployment, SSO, advanced controls, and audit automation.' },
                ].map((plan) => (
                  <div key={plan.title} style={{ background: '#fff', borderRadius: 18, padding: 20, border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 10px 24px rgba(15,23,42,0.05)' }}>
                    <div style={{ fontWeight: 800, fontSize: 18 }}>{plan.title}</div>
                    <div style={{ marginTop: 8, color: '#0369a1', fontWeight: 800, fontSize: 22 }}>{plan.price}</div>
                    <div style={{ marginTop: 10, color: '#475569', lineHeight: 1.6 }}>{plan.note}</div>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Link to="/app/dashboard" className="header-brand-link">
            <img src="/assets/vc_logo.png" alt="VoxCloud" className="header-logo" />
            <div>
              <div style={{ color: '#ffffff', fontSize: 24, fontWeight: 700, letterSpacing: '-0.03em' }}>VoxCore</div>
            </div>
          </Link>
          <WorkspaceSwitcher />
        </div>

        <UserDropdown token={localStorage.getItem('voxcore_token') || ''} onLogout={handleLogout} />
      </header>

      <div style={{ display: 'flex', minHeight: 'calc(100vh - 72px)' }}>
        <Sidebar />
        <main style={{ flex: 1, minWidth: 0, overflowY: 'auto' }}>
          <div className="page-container">
            <Routes>
              <Route path="/app/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
              <Route path="/app/databases" element={<RequireAuth><Databases /></RequireAuth>} />
              <Route path="/app/datasources" element={<RequireAuth><DataSourcesPage /></RequireAuth>} />
              <Route path="/app/datasources/new/:platform" element={<RequireAuth><DataSourceNewPage /></RequireAuth>} />
              <Route path="/app/semantic-models" element={<RequireAuth><SemanticModelsPage /></RequireAuth>} />
              <Route path="/app/semantic-models/new" element={<RequireAuth><SemanticModelsPage /></RequireAuth>} />
              <Route path="/datasources/new/:platform" element={<RequireAuth><DataSourceNewPage /></RequireAuth>} />
              <Route path="/app/policies" element={<RequireAuth><Policies /></RequireAuth>} />
              <Route path="/app/query-logs" element={<RequireAuth><QueryLogs /></RequireAuth>} />
              <Route path="/app/query-logs/:id" element={<RequireAuth><QueryInvestigation /></RequireAuth>} />
              <Route path="/app/sandbox" element={<RequireAuth><Sandbox /></RequireAuth>} />
              <Route path="/app/schema" element={<RequireAuth><SchemaExplorerPage /></RequireAuth>} />
              <Route path="/app/settings" element={<RequireAuth><SettingsPage /></RequireAuth>} />
              <Route path="/app/architecture" element={<RequireAuth><ArchitecturePage /></RequireAuth>} />
              <Route path="/app/agents" element={<RequireAuth><AgentInsightsPage /></RequireAuth>} />
              <Route path="/app/control-center" element={<RequireAuth><Suspense fallback={<div style={{ color: '#cbd5e1', padding: 24 }}>Loading control center...</div>}><ControlCenter /></Suspense></RequireAuth>} />
              <Route path="/app" element={<RequireAuth><SqlAssistant /></RequireAuth>} />
              <Route path="/dashboard" element={<RequireAuth><Navigate to="/app/dashboard" replace /></RequireAuth>} />
              <Route path="/datasources" element={<RequireAuth><Navigate to="/app/datasources" replace /></RequireAuth>} />
              <Route path="/sql" element={<RequireAuth><Navigate to="/app" replace /></RequireAuth>} />
              <Route path="/schema" element={<RequireAuth><Navigate to="/app/schema" replace /></RequireAuth>} />
              <Route path="/governance" element={<RequireAuth><Navigate to="/app/policies" replace /></RequireAuth>} />
              <Route path="/workspaces" element={<RequireAuth><Navigate to="/app/settings" replace /></RequireAuth>} />
              <Route path="/login" element={<Login onLogin={handleLogin} />} />
              <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
