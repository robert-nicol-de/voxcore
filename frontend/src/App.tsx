import React, { useState, useRef } from 'react';
import './App.css';
import Chat from './components/Chat';
import Sidebar from './components/Sidebar';
import Settings from './components/Settings';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const chatRef = useRef<{handleQuestionSelect: (q: string) => void}>(null);

  return (
    <div className="app">
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <Sidebar 
          onClose={() => setSidebarOpen(false)}
          onQuestionSelect={(question) => chatRef.current?.handleQuestionSelect(question)}
        />
      </div>

      <div className="main-content">
        <header className="app-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <div className="header-content">
            <div className="logo-section">
              <div className="voxquery-logo">
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>
                  V<span style={{ color: '#06b6d4' }}>✓</span>X
                </div>
              </div>
              <div className="app-title">
                <h1>VoxQuery</h1>
                <p>Natural Language SQL Assistant</p>
              </div>
            </div>
          </div>
          <button
            className="settings-toggle"
            onClick={() => setShowSettings(true)}
            title="Settings"
          >
            ⚙️
          </button>
        </header>

        {showSettings && <Settings onClose={() => setShowSettings(false)} />}

        <div className="chat-container">
          <Chat ref={chatRef} />
        </div>
      </div>
    </div>
  );
}

export default App;
