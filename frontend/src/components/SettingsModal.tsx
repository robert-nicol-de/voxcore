import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import './SettingsModal.css';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [accentColor, setAccentColor] = useState(localStorage.getItem('accentColor') || '#3b82f6');
  const [bgColor, setBgColor] = useState(localStorage.getItem('bgColor') || '#0f172a');
  const [textColor, setTextColor] = useState(localStorage.getItem('textColor') || '#e0e7ff');

  if (!isOpen) return null;

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const handleAccentColorChange = (color: string) => {
    setAccentColor(color);
    localStorage.setItem('accentColor', color);
    document.documentElement.style.setProperty('--primary', color);
  };

  const handleBgColorChange = (color: string) => {
    setBgColor(color);
    localStorage.setItem('bgColor', color);
    document.documentElement.style.setProperty('--bg-primary', color);
  };

  const handleTextColorChange = (color: string) => {
    setTextColor(color);
    localStorage.setItem('textColor', color);
    document.documentElement.style.setProperty('--text-light', color);
  };

  const accentPresets = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
  const bgPresets = ['#0f172a', '#1e293b', '#1a1a2e', '#16213e', '#0d1117'];
  const textPresets = ['#e0e7ff', '#f1f5f9', '#e2e8f0', '#cbd5e1', '#d1d5db'];

  const modalContent = (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="settings-close" onClick={onClose}>✕</button>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h3>Theme</h3>
            <div className="theme-options">
              <button
                className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => handleThemeChange('dark')}
              >
                🌙 Dark
              </button>
              <button
                className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                onClick={() => handleThemeChange('light')}
              >
                ☀️ Light
              </button>
            </div>
          </div>

          <div className="settings-section">
            <h3>Accent Color</h3>
            <div className="color-presets">
              {accentPresets.map(color => (
                <button
                  key={color}
                  className={`color-preset ${accentColor === color ? 'active' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleAccentColorChange(color)}
                  title={color}
                />
              ))}
            </div>
            <div className="color-input-group">
              <input
                type="color"
                value={accentColor}
                onChange={(e) => handleAccentColorChange(e.target.value)}
                className="color-input"
              />
              <span className="color-value">{accentColor}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Background Color</h3>
            <div className="color-presets">
              {bgPresets.map(color => (
                <button
                  key={color}
                  className={`color-preset ${bgColor === color ? 'active' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleBgColorChange(color)}
                  title={color}
                />
              ))}
            </div>
            <div className="color-input-group">
              <input
                type="color"
                value={bgColor}
                onChange={(e) => handleBgColorChange(e.target.value)}
                className="color-input"
              />
              <span className="color-value">{bgColor}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Text Color</h3>
            <div className="color-presets">
              {textPresets.map(color => (
                <button
                  key={color}
                  className={`color-preset ${textColor === color ? 'active' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => handleTextColorChange(color)}
                  title={color}
                />
              ))}
            </div>
            <div className="color-input-group">
              <input
                type="color"
                value={textColor}
                onChange={(e) => handleTextColorChange(e.target.value)}
                className="color-input"
              />
              <span className="color-value">{textColor}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>About</h3>
            <p className="about-text">VoxQuery v1.0</p>
            <p className="about-text">Natural Language SQL Query Builder</p>
          </div>
        </div>

        <div className="settings-footer">
          <button className="apply-btn" onClick={onClose}>
            ✓ Apply Settings
          </button>
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};
