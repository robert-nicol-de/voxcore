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
import { VoxCloudSidebar } from './components/VoxCloudSidebar';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginPage, setShowLoginPage] = useState(false);
  const navigate = useNavigate();

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
    navigate('/');
  };

  if (!isLoggedIn) {
    if (showLoginPage) {
      return <Login onLogin={handleLogin} />;
    }
    return (
      <div>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1f2937', padding: '16px' }}>
          <div style={{ color: '#fff', fontWeight: 'bold', fontSize: '1.5rem' }}>VoxCloud</div>
          <nav>
            <button
              style={{ background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', padding: '8px 16px', fontWeight: 'bold', cursor: 'pointer' }}
              onClick={() => setShowLoginPage(true)}
            >
              Login
            </button>
          </nav>
        </header>
        <main style={{ color: '#fff', background: '#111827', minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>VoxCloud Platform</h1>
          <p style={{ fontSize: '1.2rem', maxWidth: '700px', textAlign: 'center' }}>
            Inspect, validate, and control every AI-generated database query. Powered by VoxCore Query Firewall.
          </p>
        </main>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0f172a' }}>
      <VoxCloudSidebar />
      <div style={{ flex: 1, minWidth: 0 }}>
        <header style={{ display: 'flex', justifyContent: 'flex-end', padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <UserDropdown token={localStorage.getItem('voxcore_token') || ''} onLogout={handleLogout} />
        </header>
        <main style={{ padding: 12 }}>
          <Routes>
            <Route path="/app/dashboard" element={<Dashboard />} />
            <Route path="/app/databases" element={<Databases />} />
            <Route path="/app/policies" element={<Policies />} />
            <Route path="/app/query-logs" element={<QueryLogs />} />
            <Route path="/app/sandbox" element={<Sandbox />} />
            <Route path="/app" element={<SqlAssistant />} />
            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
