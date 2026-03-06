# Implementation Bridge: React + CSS Variables

**Ready-to-use CSS variables and React component templates based on VOXCORE_ENTERPRISE_DESIGN_SYSTEM_COMPLETE.md**

---

## 1. CSS VARIABLES FILE

Create: `frontend/src/styles/design-system.css`

```css
/* ============================================================================
   VOXCORE ENTERPRISE DESIGN SYSTEM - CSS VARIABLES
   ============================================================================ */

:root {
  /* ========================================================================
     SHADOWS (3-Level Enterprise Hierarchy)
     ======================================================================== */
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.12);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.16);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.20);

  /* ========================================================================
     RESPONSIVE LAYOUT TOKENS
     ======================================================================== */
  --margin-desktop: 80px;
  --margin-tablet: 64px;
  --margin-mobile: 16px;

  --gutter-desktop: 24px;
  --gutter-tablet: 20px;
  --gutter-mobile: 16px;

  --sidebar-desktop: 280px;
  --sidebar-tablet: 240px;
  --sidebar-mobile: 0;

  --header-height-desktop: 56px;
  --header-height-tablet: 48px;
  --header-height-mobile: 48px;

  /* ========================================================================
     COLORS - NEUTRALS (6 colors)
     ======================================================================== */
  --color-bg-primary: #0F172A;
  --color-surface: #1A202C;
  --color-surface-elevated: #1E293B;
  --color-border: #334155;
  --color-text-secondary: #64748B;
  --color-text-primary: #F1F5F9;

  /* ========================================================================
     COLORS - SEMANTIC (6 colors)
     ======================================================================== */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  --color-accent-primary: #6366F1;
  --color-brand: #7C3AED;

  /* ========================================================================
     COLORS - STATUS (3 colors)
     ======================================================================== */
  --color-status-passed: #10B981;
  --color-status-rewritten: #F59E0B;
  --color-status-blocked: #EF4444;

  /* ========================================================================
     TEXT HIERARCHY
     ======================================================================== */
  --color-text-heading: #F1F5F9;
  --color-text-body: #E2E8F0;
  --color-text-muted: #64748B;
  --color-text-disabled: #475569;

  /* ========================================================================
     INTERACTIVE ELEMENTS
     ======================================================================== */
  --color-button-primary: #6366F1;
  --color-button-primary-hover: #4F46E5;
  --color-button-secondary: #334155;
  --color-link: #3B82F6;

  /* ========================================================================
     SPACING (8pt System)
     ======================================================================== */
  --spacing-1: 8px;
  --spacing-2: 16px;
  --spacing-3: 24px;
  --spacing-4: 32px;
  --spacing-5: 48px;
  --spacing-6: 64px;

  /* ========================================================================
     BORDER RADIUS
     ======================================================================== */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  /* ========================================================================
     TRANSITIONS
     ======================================================================== */
  --transition-fast: 200ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
  --transition-slow: 500ms ease-in-out;

  /* ========================================================================
     RESPONSIVE DEFAULTS (Mobile-First)
     ======================================================================== */
  --margin: var(--margin-mobile);
  --gutter: var(--gutter-mobile);
  --sidebar-width: var(--sidebar-mobile);
  --header-height: var(--header-height-mobile);
}

/* ============================================================================
   TABLET BREAKPOINT (1024px+)
   ============================================================================ */
@media (min-width: 1024px) {
  :root {
    --margin: var(--margin-tablet);
    --gutter: var(--gutter-tablet);
    --sidebar-width: var(--sidebar-tablet);
    --header-height: var(--header-height-tablet);
  }
}

/* ============================================================================
   DESKTOP BREAKPOINT (1920px+)
   ============================================================================ */
@media (min-width: 1920px) {
  :root {
    --margin: var(--margin-desktop);
    --gutter: var(--gutter-desktop);
    --sidebar-width: var(--sidebar-desktop);
    --header-height: var(--header-height-desktop);
  }
}

/* ============================================================================
   GLOBAL STYLES
   ============================================================================ */

* {
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 0;
  padding: 0;
}

/* ============================================================================
   UTILITY CLASSES
   ============================================================================ */

.shadow-sm {
  box-shadow: var(--shadow-sm);
}

.shadow-md {
  box-shadow: var(--shadow-md);
}

.shadow-lg {
  box-shadow: var(--shadow-lg);
}

.text-primary {
  color: var(--color-text-primary);
}

.text-secondary {
  color: var(--color-text-secondary);
}

.text-muted {
  color: var(--color-text-muted);
}

.text-disabled {
  color: var(--color-text-disabled);
}

.bg-primary {
  background-color: var(--color-bg-primary);
}

.bg-surface {
  background-color: var(--color-surface);
}

.bg-surface-elevated {
  background-color: var(--color-surface-elevated);
}

.border-default {
  border-color: var(--color-border);
}

.rounded-sm {
  border-radius: var(--radius-sm);
}

.rounded-md {
  border-radius: var(--radius-md);
}

.rounded-lg {
  border-radius: var(--radius-lg);
}
```

---

## 2. REACT COMPONENT TEMPLATES

### Button Component

Create: `frontend/src/components/Button.tsx`

```tsx
import React from 'react';
import './Button.css';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  state?: 'default' | 'hover' | 'loading' | 'disabled';
  onClick?: () => void;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  state = 'default',
  onClick,
  className = '',
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${state} ${className}`}
      onClick={onClick}
      disabled={state === 'disabled' || state === 'loading'}
    >
      {state === 'loading' ? (
        <span className="spinner"></span>
      ) : (
        children
      )}
    </button>
  );
};
```

Create: `frontend/src/components/Button.css`

```css
.btn {
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
}

/* Primary Button */
.btn-primary {
  background-color: var(--color-button-primary);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background-color: var(--color-button-primary-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn-primary.btn-loading {
  background-color: var(--color-button-primary);
  opacity: 0.8;
  cursor: not-allowed;
}

.btn-primary.btn-disabled {
  background-color: var(--color-button-secondary);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Secondary Button */
.btn-secondary {
  background-color: var(--color-button-secondary);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
  background-color: var(--color-border);
  box-shadow: var(--shadow-md);
}

.btn-secondary.btn-disabled {
  background-color: var(--color-button-secondary);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Loading Spinner */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

### Input Component

Create: `frontend/src/components/Input.tsx`

```tsx
import React from 'react';
import './Input.css';

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  state?: 'default' | 'focused' | 'filled' | 'disabled' | 'error';
  errorMessage?: string;
  className?: string;
}

export const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  state = 'default',
  errorMessage,
  className = '',
}) => {
  return (
    <div className={`input-wrapper input-${state} ${className}`}>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={state === 'disabled'}
        className="input-field"
      />
      {state === 'error' && errorMessage && (
        <span className="error-message">{errorMessage}</span>
      )}
    </div>
  );
};
```

Create: `frontend/src/components/Input.css`

```css
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.input-field {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-2) var(--spacing-3);
  color: var(--color-text-primary);
  font-size: 15px;
  transition: all var(--transition-fast);
}

.input-field::placeholder {
  color: var(--color-text-muted);
}

.input-field:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  border-width: 2px;
  box-shadow: var(--shadow-sm), inset 0 0 0 1px rgba(99, 102, 241, 0.1);
}

/* States */
.input-default .input-field {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}

.input-focused .input-field {
  background-color: var(--color-surface);
  border: 2px solid var(--color-accent-primary);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px rgba(99, 102, 241, 0.1);
}

.input-filled .input-field {
  background-color: var(--color-surface);
  border: 1px solid var(--color-text-secondary);
}

.input-disabled .input-field {
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.5;
}

.input-error .input-field {
  background-color: var(--color-surface);
  border: 2px solid var(--color-error);
}

.error-message {
  color: var(--color-error);
  font-size: 13px;
  margin-top: var(--spacing-1);
}
```

### Card Component

Create: `frontend/src/components/Card.tsx`

```tsx
import React from 'react';
import './Card.css';

interface CardProps {
  children: React.ReactNode;
  elevation?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  elevation = 'sm',
  className = '',
}) => {
  return (
    <div className={`card card-${elevation} ${className}`}>
      {children}
    </div>
  );
};
```

Create: `frontend/src/components/Card.css`

```css
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-3);
  transition: all var(--transition-fast);
}

.card-sm {
  box-shadow: var(--shadow-sm);
}

.card-md {
  box-shadow: var(--shadow-md);
}

.card-lg {
  box-shadow: var(--shadow-lg);
}

.card:hover {
  box-shadow: var(--shadow-md);
}
```

---

## 3. LAYOUT COMPONENT

Create: `frontend/src/components/Layout.tsx`

```tsx
import React from 'react';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  sidebar,
  header,
}) => {
  return (
    <div className="layout">
      {header && <header className="layout-header">{header}</header>}
      <div className="layout-body">
        {sidebar && <aside className="layout-sidebar">{sidebar}</aside>}
        <main className="layout-content">{children}</main>
      </div>
    </div>
  );
};
```

Create: `frontend/src/components/Layout.css`

```css
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--color-bg-primary);
}

.layout-header {
  height: var(--header-height);
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 var(--margin);
  box-shadow: var(--shadow-sm);
}

.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.layout-sidebar {
  width: var(--sidebar-width);
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  padding: var(--spacing-3);
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--margin);
  gap: var(--gutter);
  display: flex;
  flex-direction: column;
}

/* Mobile: Hide sidebar by default */
@media (max-width: 1023px) {
  .layout-sidebar {
    display: none;
  }
}
```

---

## 4. IMPORT IN MAIN APP

Update: `frontend/src/App.tsx`

```tsx
import React from 'react';
import './styles/design-system.css';
import { Layout } from './components/Layout';
import { Button } from './components/Button';
import { Input } from './components/Input';
import { Card } from './components/Card';

function App() {
  const [query, setQuery] = React.useState('');

  return (
    <Layout
      header={<h1>VoxCore Platform</h1>}
      sidebar={
        <nav>
          <Button variant="secondary">Dashboard</Button>
          <Button variant="secondary">AI Activity</Button>
          <Button variant="secondary">Query Console</Button>
        </nav>
      }
    >
      <Card>
        <h2>Governance Dashboard</h2>
        <Input
          value={query}
          onChange={setQuery}
          placeholder="Enter your query..."
        />
        <Button onClick={() => console.log(query)}>
          Generate SQL
        </Button>
      </Card>
    </Layout>
  );
}

export default App;
```

---

## 5. TAILWIND CONFIGURATION (Alternative)

If using Tailwind CSS, update: `tailwind.config.js`

```js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Neutrals
        'vox-bg-primary': '#0F172A',
        'vox-surface': '#1A202C',
        'vox-surface-elevated': '#1E293B',
        'vox-border': '#334155',
        'vox-text-secondary': '#64748B',
        'vox-text-primary': '#F1F5F9',
        // Semantic
        'vox-success': '#10B981',
        'vox-warning': '#F59E0B',
        'vox-error': '#EF4444',
        'vox-info': '#3B82F6',
        'vox-accent': '#6366F1',
        'vox-brand': '#7C3AED',
      },
      boxShadow: {
        'vox-sm': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'vox-md': '0 8px 24px rgba(0, 0, 0, 0.16)',
        'vox-lg': '0 12px 32px rgba(0, 0, 0, 0.20)',
      },
      spacing: {
        'vox-1': '8px',
        'vox-2': '16px',
        'vox-3': '24px',
        'vox-4': '32px',
        'vox-5': '48px',
        'vox-6': '64px',
      },
      borderRadius: {
        'vox-sm': '8px',
        'vox-md': '12px',
        'vox-lg': '16px',
      },
    },
  },
  plugins: [],
};
```

---

**Status**: Ready for implementation  
**Quality**: Production-grade  
**Next**: Copy CSS variables file and component templates into your project
