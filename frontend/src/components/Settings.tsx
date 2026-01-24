import React, { useState } from 'react';
import './Settings.css';

interface SettingsProps {
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const [showSQL, setShowSQL] = useState(true);
  const [showResults, setShowResults] = useState(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>⚙️ Settings</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="settings-content">
          {/* Display Options */}
          <div className="settings-section">
            <h3>Display Options</h3>
            <label className="settings-checkbox">
              <input
                type="checkbox"
                checked={showSQL}
                onChange={(e) => setShowSQL(e.target.checked)}
              />
              <span>Show SQL</span>
            </label>
            <label className="settings-checkbox">
              <input
                type="checkbox"
                checked={showResults}
                onChange={(e) => setShowResults(e.target.checked)}
              />
              <span>Show Results</span>
            </label>
          </div>

          {/* Theme */}
          <div className="settings-section">
            <h3>Theme</h3>
            <div className="theme-options">
              <label className="theme-radio">
                <input
                  type="radio"
                  value="dark"
                  checked={theme === 'dark'}
                  onChange={(e) => setTheme(e.target.value as 'dark')}
                />
                <span>Dark</span>
              </label>
              <label className="theme-radio">
                <input
                  type="radio"
                  value="light"
                  checked={theme === 'light'}
                  onChange={(e) => setTheme(e.target.value as 'light')}
                />
                <span>Light</span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-footer">
          <a href="#help" className="settings-link">? Help</a>
          <a href="#docs" className="settings-link">📚 Docs</a>
        </div>
      </div>
    </div>
  );
};

export default Settings;
