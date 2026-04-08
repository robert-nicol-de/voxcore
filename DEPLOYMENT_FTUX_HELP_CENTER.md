# 🔗 DEPLOYMENT: Add Help Center to Navigation

## What You Need to Do

### Step 1: Add Route to React Router

Find your main routing file (likely `src/App.jsx` or `src/main.jsx`):

```javascript
import HelpCenter from './pages/HelpCenter';  // ← Add this import

// In your Router/Routes section:
<Route path="/help" element={<HelpCenter />} />  // ← Add this route
```

**Example (if using React Router v6):**

```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HelpCenter from './pages/HelpCenter';
import Playground from './pages/Playground';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/playground" element={<Playground />} />
        <Route path="/help" element={<HelpCenter />} />
        {/* other routes */}
      </Routes>
    </Router>
  );
}
```

---

### Step 2: Add Navigation Link

Find your navigation component (likely `src/components/Navigation.jsx` or in your header/layout):

```javascript
import { Link } from 'react-router-dom';

// In your nav menu:
<Link to="/help" className="nav-link">
  📚 Help Center
</Link>
```

**Example (if using a navbar):**

```javascript
function Navigation() {
  return (
    <nav style={{ display: 'flex', gap: 20, padding: '16px 40px' }}>
      <Link to="/" style={{ fontSize: 16, fontWeight: 600 }}>🏠 Dashboard</Link>
      <Link to="/playground" style={{ fontSize: 16, fontWeight: 600 }}>⚡ Playground</Link>
      <Link to="/audit" style={{ fontSize: 16, fontWeight: 600 }}>📋 Audit Logs</Link>
      <Link to="/help" style={{ fontSize: 16, fontWeight: 600 }}>
        📚 Help Center
      </Link>
      <Link to="/settings" style={{ fontSize: 16, fontWeight: 600 }}>⚙️ Settings</Link>
    </nav>
  );
}
```

---

### Step 3: Test It

```bash
# 1. Start dev server
npm run dev

# 2. Go to http://localhost:3000/help

# 3. You should see:
#    - Sidebar with 5 sections
#    - Main content area
#    - Dark blue theme
#    - Fully functional help content
```

---

### Step 4: Test Onboarding Flow

```bash
# 1. Go to Playground: http://localhost:3000/playground

# 2. Clear onboarding flag:
#    Open browser console (F12) and run:
localStorage.removeItem('voxcore_onboarding_dismissed');

# 3. Refresh the page

# 4. You should see:
#    - OnboardingModal (Step 1: Positioning)
#    - Click "Start with a live demo"
#    - Step 2: Environment + Data Type selector
#    - Click "Continue"
#    - Step 3: Ready state with checklist
#    - Click "Run Demo Query"
#    - Auto-executes: SELECT * FROM users
#    - Shows WowMomentOverlay (query was BLOCKED)
#    - 👉 "Try Another Query"
#    - Try: SELECT id, name FROM users LIMIT 50
#    - Shows WowMomentOverlay (query was ALLOWED)
```

---

### Step 5: Verify All Components Work

```bash
# Check these components exist and are imported:

frontend/src/components/
├── onboarding/
│   ├── OnboardingModal.jsx ✓
│   └── OnboardingModal.css ✓
├── wowmoment/
│   ├── WowMomentOverlay.jsx ✓
│   └── WowMomentOverlay.css ✓
├── help/
│   ├── HelpTooltip.jsx ✓
│   └── HelpTooltip.css ✓
└── empty/
    ├── EmptyStateQuery.jsx ✓
    └── EmptyStateQuery.css ✓

frontend/src/pages/
├── HelpCenter.jsx ✓
├── HelpCenter.css ✓
└── Playground.jsx (UPDATED) ✓
```

---

## Quick Checklist

- [ ] Route added to App.jsx
- [ ] Link added to Navigation
- [ ] Dev server running with no errors
- [ ] `/help` page loads with sidebar + content
- [ ] `/playground` onboarding modal appears
- [ ] Demo query runs and shows wow moment
- [ ] Tooltips appear on hover over Risk Score label
- [ ] Help Center sidebar navigation works
- [ ] All 5 sections (Getting Started, Risk, Decisions, Policies, Audit) clickable

---

## If You Get Errors

**Error: "Cannot find module 'HelpCenter'"**
- Check file exists: `frontend/src/pages/HelpCenter.jsx`
- Check import path is correct: `import HelpCenter from './pages/HelpCenter'`

**Error: "HelpTooltip is not defined"**
- Check file exists: `frontend/src/components/help/HelpTooltip.jsx`
- Check Playground.jsx imports it

**Onboarding modal doesn't appear**
- Clear cache: `localStorage.removeItem('voxcore_onboarding_dismissed')`
- Refresh page

**Wow Moment doesn't appear**
- Check Playground.jsx has `setShowWowMoment(true)` in polling section
- Check WowMomentOverlay component is imported

---

## Done! 🎉

Your VoxCore now has:
- ✅ 3-step onboarding (< 60 seconds to wow)
- ✅ Automatic demo query execution
- ✅ Beautiful Wow Moment overlays
- ✅ Help center with 17 articles
- ✅ Inline tooltips
- ✅ Empty state guidance
- ✅ Fully responsive design
- ✅ Dark theme + animations

**Signal to users:** This is a modern, professional product. It cares about their success.
