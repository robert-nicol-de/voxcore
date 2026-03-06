# Figma Design System - VoxCore Governance Platform 🏗️

**Complete guide to building the governance-focused design system in Figma**

---

## 📋 Overview

This guide evolves the design system from a query tool to an **AI Control Infrastructure** platform. We'll build:

1. **Color Styles** - 17 colors (same as before)
2. **Design Tokens** - Spacing, radius, typography, elevation
3. **Layout Grids** - Desktop (1440px) + Tablet (1280px)
4. **Governance Components** - Analytics cards, tables, charts, alerts
5. **Platform Layouts** - Dashboard, activity monitor, policy manager, analytics
6. **File Structure** - 5-page organized hierarchy

---

## 🎨 Step 1: Color Styles (No Changes)

**Keep all 17 colors from previous system:**

### Background Colors (4)
- BG / Primary: #0F172A
- BG / Secondary: #111827
- BG / Tertiary: #1F2937
- BG / Hover: #1E293B

### Text Colors (4)
- Text / Primary: #F9FAFB
- Text / Secondary: #D1D5DB
- Text / Muted: #9CA3AF
- Text / Disabled: #6B7280

### Accent Colors (3)
- Accent / Primary: #2563EB
- Accent / Hover: #1D4ED8
- Accent / Soft: rgba(37, 99, 235, 0.15)

### Risk Colors (3)
- Risk / Safe: #16A34A
- Risk / Warning: #F59E0B
- Risk / Danger: #DC2626

### Border Colors (2)
- Border / Default: #1F2937
- Border / Subtle: #2D3748

### Surface Color (1)
- Surface / Elevated: #1E293B

**Total: 17 color styles**

---

## 🧱 Step 2: Design Tokens (No Changes)

**Keep all tokens from previous system:**

### Elevation Tokens (3)
- Elevation / 1: Y: 4px, Blur: 16px, 10% opacity
- Elevation / 2: Y: 8px, Blur: 24px, 15% opacity
- Elevation / 3: Y: 12px, Blur: 32px, 20% opacity

### Spacing Variables (6)
- Spacing / 1: 8px
- Spacing / 2: 16px
- Spacing / 3: 24px
- Spacing / 4: 32px
- Spacing / 5: 48px
- Spacing / 6: 64px

### Radius Variables (3)
- Radius / Small: 8px
- Radius / Medium: 12px
- Radius / Large: 16px

### Typography Variables (6)
- Type / Heading XL: Inter 28px 600
- Type / Heading L: Inter 22px 600
- Type / Heading M: Inter 18px 500
- Type / Body: Inter 15px 400
- Type / Small: Inter 13px 400
- Type / Mono: JetBrains Mono 13px 400

---

## 📐 Step 3: Layout Grids (No Changes)

**Keep both frames from previous system:**

### Desktop Frame
- Size: 1440px × 900px
- Grid: 12 columns, 80px margins, 24px gutter

### Tablet Frame
- Size: 1280px × 800px
- Grid: 12 columns, 64px margins, 24px gutter

---

## 🧩 Step 4: New Governance Components

### Component A: Metric Card

**Purpose**: Display KPI (key performance indicator)

**Create frame:**
- Width: 280px
- Height: 140px
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 24px
- Shadow: Elevation / 1

**Inside (Auto Layout - Vertical):**
- Spacing: 12px

**Elements:**
1. Header row (Auto Layout - Horizontal)
   - Label: "Total Requests" (Type / Small, Text / Muted)
   - Trend icon: ↑ (green) or ↓ (red)

2. Metric value: "2,847" (Type / Heading L, Text / Primary)

3. Subtext: "+12% vs yesterday" (Type / Small, Text / Secondary)

**Component name:** "Card / Metric"

**Variants:**
- Trend: Up, Down, Neutral

---

### Component B: Risk Badge (Enhanced)

**Keep existing component but add variants:**

**Variants:**
- Level: Safe, Warning, Danger
- Size: Small (6px 12px), Medium (8px 16px), Large (12px 20px)

**Component name:** "Status / RiskBadge"

---

### Component C: Activity Table

**Purpose**: Display real-time AI activity

**Create frame:**
- Width: Fill container
- Height: Auto
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 0

**Inside (Auto Layout - Vertical):**
- Spacing: 0

**Header row:**
- Background: BG / Tertiary
- Padding: 16px 24px
- Columns: User | Prompt | SQL | Risk | Action | Time
- Font: Type / Small, Text / Secondary

**Data rows (repeating):**
- Padding: 16px 24px
- Border-bottom: 1px Border / Subtle
- Columns with data
- Hover state: BG / Hover

**Component name:** "Table / Activity"

---

### Component D: Alert Box

**Purpose**: Display system messages

**Create frame:**
- Width: Fill container
- Height: Auto
- Background: Risk / Safe (20% opacity)
- Border-left: 4px Risk / Safe
- Radius: Radius / Small
- Padding: 16px 24px

**Inside (Auto Layout - Horizontal):**
- Spacing: 12px
- Align: Center

**Elements:**
1. Icon (24×24): ✓ (for success)
2. Message text (Type / Body, Text / Primary)
3. Close button (right-aligned)

**Component name:** "Alert / Box"

**Variants:**
- Type: Success, Warning, Error, Info
- Colors adjust based on type

---

### Component E: Policy Toggle

**Purpose**: Enable/disable governance rules

**Create frame:**
- Width: Auto
- Height: 40px
- Background: Transparent

**Inside (Auto Layout - Horizontal):**
- Spacing: 12px
- Align: Center

**Elements:**
1. Label: "Allow DELETE operations" (Type / Body, Text / Primary)
2. Toggle switch (48px wide)
   - Off state: BG / Tertiary
   - On state: BG / Accent Primary

**Component name:** "Control / Toggle"

**Variants:**
- State: On, Off, Disabled

---

### Component F: Chart Card

**Purpose**: Embed charts in dashboard

**Create frame:**
- Width: Fill container
- Height: 300px
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 24px
- Shadow: Elevation / 1

**Inside (Auto Layout - Vertical):**
- Spacing: 16px

**Header:**
- Title: "Query Trends" (Type / Heading M, Text / Primary)
- Time range selector: "24h | 7d | 30d"

**Chart area:**
- Placeholder for line chart
- Background: BG / Primary
- Height: 200px

**Component name:** "Card / Chart"

**Variants:**
- ChartType: Line, Bar, Pie, Heatmap

---

### Component G: Status Indicator

**Purpose**: Show system health

**Create frame:**
- Width: Auto
- Height: Auto
- Background: Transparent

**Inside (Auto Layout - Horizontal):**
- Spacing: 8px
- Align: Center

**Elements:**
1. Dot (12×12): Green (healthy), Yellow (warning), Red (error)
2. Label: "All systems operational" (Type / Small, Text / Primary)

**Component name:** "Status / Indicator"

**Variants:**
- Health: Healthy, Warning, Error

---

### Component H: Data Access Control

**Purpose**: Configure schema whitelists

**Create frame:**
- Width: Fill container
- Height: Auto
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 24px

**Inside (Auto Layout - Vertical):**
- Spacing: 16px

**Header:**
- Title: "Schema Whitelist" (Type / Heading M)
- Add button (right-aligned)

**List of items:**
- Each item: Table name + Remove button
- Hover state: BG / Hover

**Component name:** "Control / DataAccess"

---

## 📁 Step 5: Organize File Structure

### Create 5-Page Hierarchy

```
📁 00 – Foundations
   ├─ Colors (17 color reference)
   ├─ Typography (6 type styles)
   ├─ Spacing (8pt system)
   └─ Effects (Elevation tokens)

📁 01 – Primitives
   ├─ Buttons (with states)
   ├─ Inputs (text, select, toggle)
   ├─ Badges (status indicators)
   ├─ Icons
   └─ Tables (sortable, filterable)

📁 02 – Components
   ├─ Navigation (sidebar, top bar)
   ├─ Cards (metric, chart, status)
   ├─ Alerts (warning, error, info)
   ├─ Controls (toggle, dropdown, selector)
   └─ Panels (SQL viewer, policy editor)

📁 03 – Governance Modules
   ├─ Dashboard Cards (metric, chart, status)
   ├─ Activity Table (with columns)
   ├─ Policy Form (configuration)
   ├─ Risk Chart (visualization)
   ├─ Approval Workflow (status steps)
   └─ Audit Log (compliance records)

📁 04 – Platform Layouts
   ├─ Main Layout (sidebar + content)
   ├─ Dashboard Layout (grid of cards)
   ├─ Activity Monitor Layout (table + filters)
   ├─ Policy Manager Layout (forms)
   └─ Analytics Layout (charts)

📁 05 – Screens
   ├─ Governance Dashboard
   ├─ AI Activity Monitor
   ├─ Policy Engine Manager
   ├─ Risk Analytics
   └─ Settings
```

---

## 🖼️ Page Details

### Page: 00 – Foundations / Colors

1. Create 17 rectangles (one per color)
2. Apply each color style
3. Label with color name and hex code
4. Organize in grid (4 columns)

### Page: 00 – Foundations / Effects

1. Create 3 frames showing elevation levels
2. Apply Elevation / 1, 2, 3 shadows
3. Label each with shadow values
4. Show use cases (hover, modal, floating panel)

### Page: 01 – Primitives / Tables

1. Create table component with header row
2. Add 3 data rows
3. Show hover state
4. Show sorted/filtered states

### Page: 02 – Components / Cards

1. Place Metric Card component
2. Place Chart Card component
3. Place Status Card component
4. Show all variants

### Page: 03 – Governance Modules / Dashboard Cards

1. Create 4 metric cards (2×2 grid)
   - Total Requests
   - Risk Distribution
   - Blocked Attempts
   - Policy Violations

2. Create 2 chart cards (2×1 grid)
   - Query Trends (line chart)
   - Data Access Heatmap

3. Create violations list (table)

### Page: 03 – Governance Modules / Activity Table

1. Create full-width activity table
2. Add 5 sample rows
3. Show filter controls (top)
4. Show pagination (bottom)

### Page: 03 – Governance Modules / Policy Form

1. Create form sections:
   - Risk Thresholds (sliders)
   - Allowed Operations (toggles)
   - Schema Whitelist (list + add button)
   - Masking Rules (list + add button)
   - Query Limits (input fields)

2. Add Save/Cancel buttons

### Page: 04 – Platform Layouts / Dashboard Layout

1. Create frame: 1440×900
2. Add 12-column grid
3. Place TopBar (full width)
4. Place Sidebar (240px left)
5. Place main content (fill remaining)
6. Add 4 metric cards (2×2)
7. Add 2 chart cards (2×1)
8. Add violations list

### Page: 04 – Platform Layouts / Activity Monitor Layout

1. Create frame: 1440×900
2. Add 12-column grid
3. Place TopBar (full width)
4. Place Sidebar (240px left)
5. Place filter controls (top)
6. Place activity table (fill remaining)

### Page: 05 – Screens / Governance Dashboard

1. Create full screen mockup
2. Place all dashboard components
3. Add sample data
4. Show complete user interface

### Page: 05 – Screens / AI Activity Monitor

1. Create full screen mockup
2. Place activity table with data
3. Add filter controls
4. Show real-time indicator

### Page: 05 – Screens / Policy Engine Manager

1. Create full screen mockup
2. Place policy form
3. Add all configuration sections
4. Show Save/Cancel buttons

### Page: 05 – Screens / Risk Analytics

1. Create full screen mockup
2. Place 4 chart cards
3. Add time range selector
4. Show drill-down capability

---

## ✅ Checklist

### Colors (17 total)
- [ ] 4 Background colors
- [ ] 4 Text colors
- [ ] 3 Accent colors
- [ ] 3 Risk colors
- [ ] 2 Border colors
- [ ] 1 Surface color

### Variables
- [ ] 3 Elevation tokens
- [ ] 6 Spacing variables
- [ ] 3 Radius variables
- [ ] 6 Typography variables

### Layout
- [ ] 1440px desktop frame
- [ ] 1280px tablet frame
- [ ] 12-column grid on both

### New Governance Components
- [ ] Metric Card component
- [ ] Activity Table component
- [ ] Alert Box component
- [ ] Policy Toggle component
- [ ] Chart Card component
- [ ] Status Indicator component
- [ ] Data Access Control component

### Component States
- [ ] All interactive components have states
- [ ] Metric Card: Trend variants
- [ ] Risk Badge: Level + Size variants
- [ ] Alert Box: Type variants
- [ ] Policy Toggle: On/Off/Disabled
- [ ] Status Indicator: Health variants

### Organization
- [ ] 5 pages created
- [ ] Components organized by category
- [ ] Color reference page
- [ ] Elevation reference page
- [ ] Governance modules page
- [ ] Platform layouts page
- [ ] Screen mockups page

---

## 🎯 Design Philosophy

### Controlled
- Structured grid layouts
- Predictable data presentation
- Clear governance rules

### Structured
- Organized information hierarchy
- Consistent component patterns
- Logical navigation flow

### Calm
- Professional color palette
- Minimal animations
- Clear status indicators

### Transparent
- Visible governance rules
- Audit trail of all actions
- Clear risk communication

---

## 🚀 Next Steps

1. **Create all 17 color styles** (same as before)
2. **Set up all design tokens** (same as before)
3. **Configure both layout grids** (same as before)
4. **Build new governance components** (8 new components)
5. **Create governance modules page** (dashboard cards, tables, forms)
6. **Build platform layouts** (all 4 screen layouts)
7. **Create screen mockups** (all 5 screens)
8. **Share with team** (enable view access)

---

**Status**: Ready for implementation  
**Quality**: Enterprise-grade  
**Scope**: Governance-focused platform design system
