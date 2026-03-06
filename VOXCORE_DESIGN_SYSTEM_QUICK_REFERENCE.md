# VoxCore Enterprise Design System - Quick Reference

**One-page cheat sheet for designers and developers**

---

## 🎨 Color Palette (17 Colors)

### Neutrals (6)
```
#0F172A  Background (Deep trust)
#1A202C  Surface (Cards, panels)
#1E293B  Surface/Elevated (Modals, floating)
#334155  Border (Subtle dividers)
#64748B  Text Secondary (Help, metadata)
#F1F5F9  Text Primary (High contrast)
```

### Semantic (6)
```
#10B981  Success (✓ Passed)
#F59E0B  Warning (⚠ Rewritten)
#EF4444  Error (✗ Blocked)
#3B82F6  Info (ℹ Information)
#6366F1  Primary (Interactive)
#7C3AED  Brand (VoxCore purple)
```

### Status (3)
```
#10B981  Passed
#F59E0B  Rewritten
#EF4444  Blocked
```

---

## 📏 Shadows (3 Levels)

```css
--shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.12);    /* Cards */
--shadow-md: 0 8px 24px rgba(0, 0, 0, 0.16);    /* Dropdowns */
--shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.20);   /* Modals */
```

---

## 📐 Spacing & Layout

### Desktop (1920px)
- Margin: 80px
- Gutter: 24px
- Sidebar: 280px
- Header: 56px

### Tablet (1280px)
- Margin: 64px
- Gutter: 20px
- Sidebar: 240px (collapsible)
- Header: 48px

### Mobile (375px)
- Margin: 16px
- Gutter: 16px
- Sidebar: Overlay
- Header: 48px

---

## 🧩 Component States

### Button
| State | Background | Text | Shadow | Transform |
|-------|-----------|------|--------|-----------|
| Default | #6366F1 | #F1F5F9 | shadow-sm | none |
| Hover | #4F46E5 | #F1F5F9 | shadow-md | -2px |
| Loading | #6366F1 | hidden | none | none |
| Disabled | #334155 | #475569 | none | none |

### Input
| State | Border | Background | Text |
|-------|--------|-----------|------|
| Default | #334155 | #1A202C | #E2E8F0 |
| Focused | #6366F1 (2px) | #1A202C | #F1F5F9 |
| Filled | #475569 | #1A202C | #F1F5F9 |
| Error | #EF4444 (2px) | #1A202C | #F1F5F9 |
| Disabled | #334155 | #0F172A | #475569 |

### SidebarItem
| State | Background | Text | Border |
|-------|-----------|------|--------|
| Default | Transparent | #E2E8F0 | none |
| Hover | rgba(99,102,241,0.1) | #F1F5F9 | none |
| Active | rgba(99,102,241,0.2) | #6366F1 | 3px left |
| Disabled | Transparent | #475569 | none |

---

## 📑 Figma Organization (5 Pages)

```
00 – Foundations
    ├─ Colors (17 reference)
    ├─ Typography
    ├─ Spacing
    └─ Effects (Elevation)

01 – Primitives
    ├─ Button (all states)
    ├─ Input (all states)
    ├─ Checkbox
    ├─ Radio
    ├─ Switch
    ├─ Badge
    ├─ Label
    └─ Help text

02 – Composite
    ├─ Card
    ├─ Panel
    ├─ Modal
    ├─ Alert/Toast
    ├─ Dropdown
    ├─ Form group
    ├─ Navigation bar
    └─ Sidebar

03 – Layouts
    ├─ Dashboard
    ├─ Query executor
    ├─ Admin panel
    ├─ Login
    └─ Error page

04 – Usage Guide
    ├─ Component API
    ├─ Code examples
    ├─ Accessibility
    ├─ Performance
    └─ Do's & don'ts
```

---

## ✨ Design Principles

| Principle | Meaning | Application |
|-----------|---------|-------------|
| **Controlled** | Consistent, rule-based | Same colors, shadows, spacing everywhere |
| **Structured** | Organized, hierarchical | Clear hierarchy, documented states |
| **Calm** | Muted, professional | No bright neons, subtle shadows |
| **Transparent** | Clear intent, visible state | Loading states, error messages visible |

---

## 🚀 Implementation Order

### Week 1: Core Components
- [ ] Button (all states)
- [ ] Input (all states)
- [ ] Card
- [ ] Badge

### Week 2: Composite
- [ ] Modal
- [ ] Sidebar
- [ ] Navigation bar
- [ ] Alert/Toast

### Week 3: Layouts
- [ ] Dashboard layout
- [ ] Query executor layout
- [ ] Admin layout

### Week 4-5: Polish & Deploy
- [ ] Micro-interactions
- [ ] Accessibility (WCAG AAA)
- [ ] Responsive testing
- [ ] Storybook + deploy

---

## 📊 Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| **Designer** | Component reuse | >80% |
| **Designer** | Design time | -40% |
| **Developer** | Implementation time | -50% |
| **Developer** | Styling bugs | -70% |
| **User** | Task completion | >90% |
| **User** | Time to find feature | <30s |
| **Business** | Feature delivery | +60% |
| **Business** | Team adoption | >90% |

---

## 🎯 CSS Variables Template

```css
:root {
  /* Colors */
  --color-background: #0F172A;
  --color-surface: #1A202C;
  --color-surface-elevated: #1E293B;
  --color-border: #334155;
  --color-text-primary: #F1F5F9;
  --color-text-secondary: #64748B;
  
  /* Semantic */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  --color-primary: #6366F1;
  
  /* Shadows */
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.12);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.16);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.20);
  
  /* Spacing */
  --margin: 80px;
  --gutter: 24px;
  --sidebar-width: 280px;
  
  /* Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

@media (max-width: 1280px) {
  :root {
    --margin: 64px;
    --gutter: 20px;
    --sidebar-width: 240px;
  }
}

@media (max-width: 375px) {
  :root {
    --margin: 16px;
    --gutter: 16px;
    --sidebar-width: 0;
  }
}
```

---

## 📚 Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| **VOXCORE_ENTERPRISE_DESIGN_SYSTEM_COMPLETE.md** | Full spec (10 sections) | Everyone |
| **IMPLEMENTATION_BRIDGE_REACT_CSS_VARIABLES.md** | React templates + CSS | Developers |
| **VOXCORE_PLATFORM_ECOSYSTEM_SPEC.md** | Platform architecture | Product/Eng |
| **VOXCORE_PLATFORM_QUICK_START.md** | Strategic overview | Leadership |
| **FIGMA_GOVERNANCE_PLATFORM_DESIGN_SYSTEM.md** | Figma setup guide | Designers |
| **VOXCORE_DESIGN_SYSTEM_QUICK_REFERENCE.md** | This cheat sheet | Everyone |

---

## 🔗 Quick Links

**Full Documentation**:
- `VOXCORE_ENTERPRISE_DESIGN_SYSTEM_COMPLETE.md` - Complete spec

**Implementation**:
- `IMPLEMENTATION_BRIDGE_REACT_CSS_VARIABLES.md` - React + CSS ready-to-use

**Design**:
- `FIGMA_GOVERNANCE_PLATFORM_DESIGN_SYSTEM.md` - Figma setup

**Strategy**:
- `VOXCORE_PLATFORM_ECOSYSTEM_SPEC.md` - Platform architecture
- `VOXCORE_PLATFORM_QUICK_START.md` - Quick overview

---

## ✅ Checklist

### Colors
- [ ] 17 colors defined
- [ ] CSS variables created
- [ ] Figma color styles created

### Components
- [ ] Button (all states)
- [ ] Input (all states)
- [ ] Card
- [ ] Modal
- [ ] Sidebar
- [ ] Navigation bar
- [ ] Alert/Toast
- [ ] Badge

### Layouts
- [ ] Desktop (1920px)
- [ ] Tablet (1280px)
- [ ] Mobile (375px)

### Quality
- [ ] Accessibility (WCAG AAA)
- [ ] Responsive testing
- [ ] Storybook documentation
- [ ] Component library packaged

---

**Status**: Production-ready ✅  
**Quality**: Enterprise-grade  
**Last Updated**: February 28, 2026
