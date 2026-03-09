import React, { useState, useEffect } from 'react';
import DemoMode from './components/DemoMode';
import './App.css';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import SchemaExplorer from './components/SchemaExplorer';
import { GovernanceDashboard } from './screens/GovernanceDashboard';
import { Login } from './screens/Login';
import { QueryHistory } from './components/QueryHistory';
import { GovernanceLogs } from './components/GovernanceLogs';
import { PoliciesManager } from './components/PoliciesManager';

type ViewType = 'dashboard' | 'query' | 'history' | 'logs' | 'policies' | 'schema';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isPreviewMode, setIsPreviewMode] = useState(true); // Preview mode enabled by default
  const [isDemoMode, setIsDemoMode] = useState(false);
  const chatRef = React.useRef<any>(null);

  // Check for demo mode from URL parameter
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const demoParam = params.get('demo');
    if (demoParam === 'true') {
      setIsDemoMode(true);
    }
  }, []);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const handleNavigate = (view: ViewType) => {
    setCurrentView(view);
    console.log('Navigating to:', view);
  };

  const [userName, setUserName] = useState<string>('');

  const handleLogin = (name?: string) => {
    setIsLoggedIn(true);
    if (name) setUserName(name);
  };

  const handleQuestionSelect = (question: string) => {
    // Navigate to query view and pass question to Chat
    setCurrentView('query');
    if (chatRef.current) {
      chatRef.current.handleQuestionSelect(question);
    }
  };

  // Show demo mode if demo=true in URL (skip login entirely)
  if (isDemoMode) {
    return <DemoMode />;
  }

  // Show login screen if not logged in
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app" data-theme={theme}>
      <div className={`sidebar ${!sidebarOpen ? 'closed' : ''}`}>
        <Sidebar 
          currentView={currentView}
          onNavigate={handleNavigate}
          onQuestionSelect={handleQuestionSelect}
          isOpen={sidebarOpen}
          onToggle={toggleSidebar}
        />
      </div>

      <div className="main-content">
        <header className="app-header">
          <button
            className="sidebar-toggle"
            onClick={toggleSidebar}
            aria-label="Toggle sidebar"
          >
            ☰
          </button>
          <div className="header-right">
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <div className="user-menu">
              <span>{isDemoMode ? '👤 Demo User' : 'Robert Nicol'}</span>
            </div>
          </div>
        </header>

        <main className="chat-container">
          {/* Dashboard View */}
          {currentView === 'dashboard' && (
            <GovernanceDashboard onAskQuestion={() => handleNavigate('query')} />
          )}

          {/* Query View */}
          {currentView === 'query' && (
            <Chat
              ref={chatRef}
              onBackToDashboard={() => handleNavigate('dashboard')}
              isPreviewMode={isPreviewMode}
            />
          )}

          {/* History View */}
          {currentView === 'history' && (
            <div className="view-content">
              <QueryHistory />
            </div>
          )}

          {/* Logs View */}
          {currentView === 'logs' && (
            <div className="view-content">
              <GovernanceLogs />
            </div>
          )}

          {/* Policies View */}
          {currentView === 'policies' && (
            <div className="view-content">
              <PoliciesManager />
            </div>
          )}

          {/* Schema View */}
          {currentView === 'schema' && (
            <SchemaExplorer onClose={() => handleNavigate('query')} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
