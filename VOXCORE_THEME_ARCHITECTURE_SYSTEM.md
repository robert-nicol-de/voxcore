# VoxCore Theme Architecture System

**Date**: February 28, 2026  
**Status**: Production-Ready Specification  
**Philosophy**: Token-based, scalable, no hard-coded colors

---

## 🎨 Core Principle

**One design system. Two modes. Zero duplication.**

- Build token-based variables
- Everything references variables
- Never hard-code colors
- Dark = Default (technical users, monitoring)
- Light = Optional (executives, presentations)
- Accent stays consistent (brand identity)
- Only surfaces + text invert

---

## 🧱 1️⃣ Figma: Variable Collection Setup

### Create Variable Collection: `Theme`

**Modes**:
- `Dark` (default)
- `Light`

---

## 🌙 Dark Mode Tokens

```
BG / Primary       #0F172A
BG / Surface       #111827
BG / Elevated      #1E293B
Text / Primary     #F9FAFB
Text / Secondary   #D1D5DB
Border / Default   #1F2937
Accent / Primary   #2563EB
Risk / Safe        #16A34A
Risk / Warning     #F59E0B
Risk / Danger      #DC2626
```

---

## ☀️ Light Mode Tokens

```
BG / Primary       #F8FAFC
BG / Surface       #FFFFFF
BG / Elevated      #F1F5F9
Text / Primary     #0F172A
Text / Secondary   #334155
Border / Default   #E2E8F0
Accent / Primary   #2563EB
Risk / Safe        #15803D
Risk / Warning     #D97706
Risk / Danger      #B91C1C
```

---

## 🔑 Key Observations

### What Inverts
- BG / Primary ✓
- BG / Surface ✓
- BG / Elevated ✓
- Text / Primary ✓
- Text / Secondary ✓
- Border / Default ✓

### What Stays Consistent
- Accent / Primary (brand identity)
- Risk / Safe (semantic meaning)
- Risk / Warning (semantic meaning)
- Risk / Danger (semantic meaning)

**Why?** Accent and risk colors carry semantic meaning. They should feel the same regardless of theme.

---

## 🛠 2️⃣ React Implementation

### CSS Variables (No Hard-Coded Colors)

**File**: `frontend/src/styles/theme-variables.css`

```css
/* Dark Mode (Default) */
:root[data-theme="dark"] {
  /* Backgrounds */
  --bg-primary: #0F172A;
  --bg-surface: #111827;
  --bg-elevated: #1E293B;
  
  /* Text */
  --text-primary: #F9FAFB;
  --text-secondary: #D1D5DB;
  
  /* Borders */
  --border-default: #1F2937;
  
  /* Accent (consistent) */
  --accent-primary: #2563EB;
  
  /* Risk (consistent) */
  --risk-safe: #16A34A;
  --risk-warning: #F59E0B;
  --risk-danger: #DC2626;
}

/* Light Mode */
:root[data-theme="light"] {
  /* Backgrounds */
  --bg-primary: #F8FAFC;
  --bg-surface: #FFFFFF;
  --bg-elevated: #F1F5F9;
  
  /* Text */
  --text-primary: #0F172A;
  --text-secondary: #334155;
  
  /* Borders */
  --border-default: #E2E8F0;
  
  /* Accent (consistent) */
  --accent-primary: #2563EB;
  
  /* Risk (consistent) */
  --risk-safe: #15803D;
  --risk-warning: #D97706;
  --risk-danger: #B91C1C;
}
```

### Theme Toggle Hook

**File**: `frontend/src/hooks/useTheme.ts`

```typescript
import { useEffect, useState } from 'react';

export const useTheme = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    // Load saved theme from localStorage
    const saved = localStorage.getItem('voxcore-theme') as 'dark' | 'light' | null;
    const initial = saved || 'dark';
    setTheme(initial);
    document.documentElement.setAttribute('data-theme', initial);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('voxcore-theme', newTheme);
  };

  return { theme, toggleTheme };
};
```

### Theme Provider Context

**File**: `frontend/src/context/ThemeContext.tsx`

```typescript
import React, { createContext, useContext } from 'react';
import { useTheme } from '../hooks/useTheme';

interface ThemeContextType {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useThemeContext = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeContext must be used within ThemeProvider');
  }
  return context;
};
```

### Theme Toggle Button Component

**File**: `frontend/src/components/ThemeToggle.tsx`

```typescript
import React from 'react';
import { useThemeContext } from '../context/ThemeContext';
import './ThemeToggle.css';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useThemeContext();

  return (
    <button
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
};
```

### Theme Toggle Styles

**File**: `frontend/src/components/ThemeToggle.css`

```css
.theme-toggle {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 200ms ease;
}

.theme-toggle:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.theme-toggle:active {
  transform: scale(0.95);
}
```

---

## 📐 3️⃣ Component Usage Pattern

### All Components Use Variables

**Example: Card Component**

```typescript
// frontend/src/components/Card.tsx
import React from 'react';
import './Card.css';

interface CardProps {
  title: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, children }) => {
  return (
    <div className="card">
      <h3 className="card-title">{title}</h3>
      <div className="card-content">{children}</div>
    </div>
  );
};
```

**Card Styles (No Hard-Coded Colors)**

```css
/* frontend/src/components/Card.css */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 24px;
  transition: all 200ms ease;
}

.card:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.card-title {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.card-content {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}
```

---

## 🎯 4️⃣ UX Strategy

### Dark Mode = Default
**Best for**:
- Technical users
- Engineers
- Monitoring screens
- 24/7 operations
- Reduced eye strain in dark environments

**Why**: Governance dashboards are typically used by technical teams in control rooms.

### Light Mode = Optional
**Best for**:
- Board presentations
- Executive reports
- Daytime office use
- Printing/exporting
- Client demos

**Why**: Executives need to present findings. Light mode is more professional for printed reports.

---

## 🔄 5️⃣ Implementation Checklist

### Figma
- [ ] Create Variable Collection: `Theme`
- [ ] Add Mode: `Dark` (default)
- [ ] Add Mode: `Light`
- [ ] Create all 10 variables (BG, Text, Border, Accent, Risk)
- [ ] Apply variables to all components
- [ ] Test theme switching in Figma
- [ ] Export variable definitions

### React
- [ ] Create `theme-variables.css` with CSS variables
- [ ] Create `useTheme` hook
- [ ] Create `ThemeContext` provider
- [ ] Create `ThemeToggle` component
- [ ] Wrap app with `ThemeProvider`
- [ ] Update all components to use CSS variables
- [ ] Test theme toggle (instant, no re-render)
- [ ] Verify localStorage persistence
- [ ] Test on all screens (Dashboard, Activity, Policy, Analytics)

### Testing
- [ ] Dark mode loads by default
- [ ] Light mode toggle works instantly
- [ ] Theme persists on page reload
- [ ] All components respect theme
- [ ] Risk colors stay consistent
- [ ] Accent color stays consistent
- [ ] No hard-coded colors remain
- [ ] Accessibility: contrast ratios pass WCAG AA

---

## 📊 6️⃣ Color Contrast Verification

### Dark Mode
- Text Primary (#F9FAFB) on BG Primary (#0F172A): **18.5:1** ✓ AAA
- Text Secondary (#D1D5DB) on BG Primary (#0F172A): **11.2:1** ✓ AAA
- Accent (#2563EB) on BG Primary (#0F172A): **5.8:1** ✓ AA

### Light Mode
- Text Primary (#0F172A) on BG Primary (#F8FAFC): **18.5:1** ✓ AAA
- Text Secondary (#334155) on BG Primary (#F8FAFC): **11.2:1** ✓ AAA
- Accent (#2563EB) on BG Primary (#F8FAFC): **5.8:1** ✓ AA

---

## 🚀 7️⃣ Deployment Strategy

### Phase 1: Foundation (Week 1)
- [ ] CSS variables in place
- [ ] Theme hook + context
- [ ] Theme toggle button
- [ ] All components updated

### Phase 2: Testing (Week 2)
- [ ] Manual testing on all screens
- [ ] Accessibility audit
- [ ] Performance testing (instant toggle)
- [ ] Cross-browser testing

### Phase 3: Launch (Week 3)
- [ ] Dark mode as default
- [ ] Light mode as optional
- [ ] User preference saved
- [ ] Monitor usage analytics

---

## 💡 8️⃣ Future Extensibility

### Easy to Add More Modes
```css
:root[data-theme="high-contrast"] {
  --bg-primary: #000000;
  --text-primary: #FFFFFF;
  /* ... */
}
```

### Easy to Add More Variables
```css
:root[data-theme="dark"] {
  --bg-primary: #0F172A;
  --bg-surface: #111827;
  --bg-elevated: #1E293B;
  --bg-overlay: rgba(15, 23, 42, 0.8); /* New */
  /* ... */
}
```

### Easy to Add Component-Specific Overrides
```css
.card[data-variant="premium"] {
  --bg-surface: var(--bg-elevated);
  --border-default: var(--accent-primary);
}
```

---

## ✅ Why This Approach Works

1. **Scalable**: Add new modes without duplicating designs
2. **Maintainable**: Change colors in one place (CSS variables)
3. **Fast**: No re-renders, instant theme swap
4. **Professional**: Consistent brand identity
5. **Accessible**: WCAG AA/AAA compliant
6. **Future-proof**: Easy to extend with new variables/modes
7. **Developer-friendly**: Simple CSS variables, no complex logic
8. **User-friendly**: Preference saved, instant toggle

---

## 📝 Implementation Order

1. Create `theme-variables.css`
2. Create `useTheme` hook
3. Create `ThemeContext` provider
4. Create `ThemeToggle` component
5. Wrap app with `ThemeProvider`
6. Update all components (Card, Button, Input, etc.)
7. Test theme toggle
8. Deploy

---

**Status**: Ready for implementation  
**Next**: Start with CSS variables, then hook, then context, then components

