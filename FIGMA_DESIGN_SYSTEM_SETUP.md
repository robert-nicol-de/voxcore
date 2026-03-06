# Figma Design System Setup - VoxQuery 🎨

**Complete guide to building the VoxQuery design system in Figma**

---

## 📋 Overview

This guide walks you through creating a production-ready design system in Figma that matches the VoxCore theme. We'll build:

1. **Color Styles** - All colors with proper naming
2. **Design Tokens** - Spacing, radius, typography
3. **Layout Grid** - 12-column responsive grid
4. **Components** - Reusable UI elements
5. **File Structure** - Organized workspace

---

## 🎨 Step 1: Create Color Styles

### In Figma:
1. Open your VoxQuery file
2. Go to **Assets** panel (left sidebar)
3. Click **Local Styles** tab
4. Click **+** to create new color style

### Background Colors

Create these 4 color styles:

| Name | Color | RGB |
|------|-------|-----|
| BG / Primary | #0F172A | 15, 23, 42 |
| BG / Secondary | #111827 | 17, 24, 39 |
| BG / Tertiary | #1F2937 | 31, 41, 55 |
| BG / Hover | #1E293B | 30, 41, 59 |

**Steps for each:**
1. Create rectangle
2. Set fill color
3. Right-click fill → "Create color style"
4. Name it exactly (e.g., "BG / Primary")
5. Delete rectangle

### Text Colors

Create these 4 color styles:

| Name | Color | RGB |
|------|-------|-----|
| Text / Primary | #F9FAFB | 249, 250, 251 |
| Text / Secondary | #D1D5DB | 209, 213, 219 |
| Text / Muted | #9CA3AF | 156, 163, 175 |
| Text / Disabled | #6B7280 | 107, 114, 128 |

### Accent Colors

Create these 3 color styles:

| Name | Color | RGB |
|------|-------|-----|
| Accent / Primary | #2563EB | 37, 99, 235 |
| Accent / Hover | #1D4ED8 | 29, 78, 216 |
| Accent / Soft | rgba(37, 99, 235, 0.15) | 37, 99, 235, 15% |

### Risk Colors

Create these 3 color styles:

| Name | Color | RGB |
|------|-------|-----|
| Risk / Safe | #16A34A | 22, 163, 74 |
| Risk / Warning | #F59E0B | 245, 158, 11 |
| Risk / Danger | #DC2626 | 220, 38, 38 |

### Border Colors

Create these 2 color styles:

| Name | Color | RGB |
|------|-------|-----|
| Border / Default | #1F2937 | 31, 41, 55 |
| Border / Subtle | #2D3748 | 45, 55, 72 |

### Surface Colors

Create this 1 color style:

| Name | Color | RGB |
|------|-------|-----|
| Surface / Elevated | #1E293B | 30, 41, 59 |

**Why?** Modals, dropdowns, and floating panels need distinct elevation. Prevents reusing BG/Tertiary incorrectly.

**Total: 17 color styles created**

---

## 🧱 Step 2: Create Design Tokens (Variables)

### In Figma:
1. Go to **Assets** panel
2. Click **Variables** tab
3. Click **+** to create new variable collection
4. Name it "VoxQuery Design Tokens"

### Elevation Tokens (Shadow Effects)

Create these 3 elevation variables for layering:

| Name | Y Offset | Blur | Opacity | Usage |
|------|----------|------|---------|-------|
| Elevation / 1 | 4px | 16px | 10% | Subtle hover states |
| Elevation / 2 | 8px | 24px | 15% | Modals, dropdowns |
| Elevation / 3 | 12px | 32px | 20% | Floating panels, tooltips |

**Why?** Enterprise UI without elevation feels flat and cheap. Controlled elevation builds trust and visual hierarchy.

**Steps:**
1. Click **+** in Variables tab
2. Select "Shadow" type
3. Name: "Elevation / 1"
4. Set Y: 4px, Blur: 16px, Color: #000000 at 10% opacity
5. Repeat for Elevation / 2 and / 3

---

## Design Tokens (Continued)

### In Figma:
1. Go to **Assets** panel
2. Click **Variables** tab
3. Click **+** to create new variable collection
4. Name it "VoxQuery Design Tokens"

### Spacing Variables (8pt System)

Create these 6 spacing variables (for layout and component padding):

| Name | Value | Usage |
|------|-------|-------|
| Spacing / 1 | 8px | Micro spacing |
| Spacing / 2 | 16px | Small spacing |
| Spacing / 3 | 24px | Medium spacing |
| Spacing / 4 | 32px | Large spacing |
| Spacing / 5 | 48px | Extra large |
| Spacing / 6 | 64px | Huge spacing |

**Steps:**
1. Click **+** in Variables tab
2. Select "Spacing" type
3. Name: "Spacing / 1"
4. Value: 8
5. Repeat for all 6

### Radius Variables

Create these 3 radius variables:

| Name | Value | Usage |
|------|-------|-----|
| Radius / Small | 8px | Small elements |
| Radius / Medium | 12px | Main elements |
| Radius / Large | 16px | Large elements |

### Typography Variables (Optional)

Create these 6 typography variables:

| Name | Font | Size | Weight |
|------|------|------|--------|
| Type / Heading XL | Inter | 28px | 600 |
| Type / Heading L | Inter | 22px | 600 |
| Type / Heading M | Inter | 18px | 500 |
| Type / Body | Inter | 15px | 400 |
| Type / Small | Inter | 13px | 400 |
| Type / Mono | JetBrains Mono | 13px | 400 |

---

## 📐 Step 3: Setup Layout Grid

### Create Main Desktop Frame

1. Create new frame: **1440px × 900px**
2. Name it: "Desktop - 1440"
3. Set background: BG / Primary color style

### Add Grid

1. Select frame
2. Go to **Design** panel (right sidebar)
3. Scroll to **Grids**
4. Click **+** to add grid
5. Configure:
   - **Type**: Columns
   - **Count**: 12
   - **Margin**: 80px (left & right)
   - **Gutter**: 24px
   - **Color**: Border / Default (20% opacity)

### Result
- 12 equal columns
- 80px margins on sides
- 24px gap between columns
- Matches Tailwind grid system

### Create Tablet Frame

1. Create new frame: **1280px × 800px**
2. Name it: "Tablet - 1280"
3. Set background: BG / Primary color style

### Add Grid to Tablet

1. Select frame
2. Go to **Design** panel (right sidebar)
3. Scroll to **Grids**
4. Click **+** to add grid
5. Configure:
   - **Type**: Columns
   - **Count**: 12
   - **Margin**: 64px (left & right)
   - **Gutter**: 24px
   - **Color**: Border / Default (20% opacity)

### Result
- 12 equal columns (responsive)
- 64px margins on sides (tablet-optimized)
- 24px gap between columns
- Future-proofs responsiveness early without designing mobile

## 🧩 Step 4: Build Components

### Component A: Top Navigation

**Create frame:**
- Width: 1440px
- Height: 64px
- Background: BG / Secondary
- Padding: 24px left/right

**Inside (Auto Layout - Horizontal):**
- Justify: Space Between
- Spacing: 16px

**Left section:**
- Logo text: "VoxQuery" (Type / Heading M)
- Environment badge: "Production" (small pill)

**Right section:**
- Notification icon (24×24)
- Avatar circle (40×40)

**Make Component:**
1. Select all elements
2. Right-click → "Create component"
3. Name: "Navigation / TopBar"

### Component B: Sidebar Item

**Create frame:**
- Width: 240px
- Height: Auto
- Padding: 12px 16px
- Radius: Radius / Small
- Background: Transparent (default)

**Inside (Auto Layout - Horizontal):**
- Spacing: 12px
- Align: Center

**Elements:**
- Icon (18×18)
- Label text (Type / Body)

**Create Variants:**
1. Right-click component → "Add variant"
2. Create property: "State"
3. Add values: Default, Hover, Active

**Variant styles:**
- **Default**: BG / Transparent, Text / Secondary
- **Hover**: BG / Hover, Text / Primary
- **Active**: BG / Accent Primary, Text / White

**Component name:** "Navigation / SidebarItem"

### Component States & Variants

All interactive components need multiple states to handle user interactions and loading states:

**SidebarItem States:**
- **Default**: BG / Transparent, Text / Secondary
- **Hover**: BG / Hover, Text / Primary (user hovers over item)
- **Active**: BG / Accent Primary, Text / White (current page)
- **Disabled**: BG / Transparent, Text / Disabled (unavailable)

**Button States:**
- **Default**: BG / Accent Primary, Text / White
- **Hover**: BG / Accent Hover, Text / White (user hovers)
- **Loading**: BG / Accent Primary (50% opacity), spinner icon, disabled interaction
- **Disabled**: BG / Tertiary, Text / Disabled (unavailable)

**Why?** Enterprise tools need loading states. Loading states reduce user anxiety and communicate that the system is working.

---

**Create frame:**
- Width: Fill container
- Height: Auto
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 24px

**Inside (Auto Layout - Vertical):**
- Spacing: 16px

**Elements:**
1. Textarea (placeholder: "Ask a question...")
   - Background: BG / Primary
   - Border: 1px Border / Subtle
   - Radius: Radius / Small
   - Padding: 16px
   - Font: Type / Body

2. Footer row (Auto Layout - Horizontal)
   - Justify: Space Between
   - Hint text (left): Type / Small, Text / Muted
   - Button (right): "Generate SQL"

**Component name:** "Card / QueryInput"

### Component D: Risk Badge

**Create frame:**
- Width: Auto
- Height: Auto
- Padding: 6px 12px
- Radius: 999px (pill shape)
- Background: Risk / Safe (default)

**Inside (Auto Layout - Horizontal):**
- Spacing: 6px
- Align: Center

**Elements:**
1. Icon (12×12): "✓"
2. Label text (Type / Small): "SAFE"

**Create Variants:**
1. Property: "Level"
2. Values: Safe, Warning, Danger

**Variant styles:**
- **Safe**: BG = Risk / Safe (15% opacity), Text = Risk / Safe
- **Warning**: BG = Risk / Warning (15% opacity), Text = Risk / Warning
- **Danger**: BG = Risk / Danger (15% opacity), Text = Risk / Danger

**Component name:** "Status / RiskBadge"

### Component E: SQL Panel

**Create frame:**
- Width: Fill container
- Height: Auto
- Background: BG / Secondary
- Border: 1px Border / Default
- Radius: Radius / Medium
- Padding: 24px

**Inside (Auto Layout - Vertical):**
- Spacing: 16px

**Header row (Auto Layout - Horizontal):**
- Justify: Space Between
- Title: "Generated SQL" (Type / Heading M)
- Risk badge (component)

**Code area:**
- Background: BG / Primary
- Border: 1px Border / Subtle
- Radius: Radius / Small
- Padding: 16px
- Font: Type / Mono
- Text: Text / Secondary
- Min height: 200px

**Component name:** "Panel / SQLViewer"

---

## 📁 Step 5: Organize File Structure

### Create Pages

In Figma, create these 5 pages with organized hierarchy:

```
📁 00 – Foundations
   ├─ Colors
   ├─ Typography
   ├─ Spacing
   └─ Effects (Elevation Tokens)

📁 01 – Primitives
   ├─ Buttons
   ├─ Inputs
   ├─ Badges
   └─ Icons

📁 02 – Components
   ├─ Navigation
   ├─ Cards
   ├─ Status
   └─ Panels

📁 03 – Layouts
   ├─ App Layout (Desktop)
   ├─ App Layout (Tablet)
   └─ Dashboard

📁 04 – Screens
   ├─ Login
   ├─ Dashboard
   ├─ Ask Query
   └─ Governance Logs
```

**Why?** This 5-page structure scales cleaner than 4 pages. "Primitives" separates atomic components (buttons, inputs) from composite components (cards, panels), making the system easier to navigate and maintain.

### Page: 00 – Foundations / Colors

Create a color reference page:

1. Create 17 rectangles (one per color)
2. Apply each color style
3. Label with color name and hex code
4. Organize in grid

### Page: 00 – Foundations / Effects

Create an elevation reference page:

1. Create 3 frames showing elevation levels
2. Apply Elevation / 1, 2, 3 shadows
3. Label each with shadow values (Y offset, blur, opacity)
4. Show use cases (hover, modal, floating panel)

### Page: 01 – Primitives / Buttons

1. Create button component with all states
2. Show: Default, Hover, Loading, Disabled
3. Include primary and secondary variants

### Page: 01 – Primitives / Inputs

1. Create input field component
2. Show: Default, Focused, Filled, Disabled, Error states

### Page: 02 – Components / Navigation

1. Place TopBar component
2. Place SidebarItem component with all variants (Default, Hover, Active, Disabled)
3. Show state transitions

### Page: 02 – Components / Cards

1. Place QueryInput card component
2. Place other card variants
3. Show with and without elevation

### Page: 03 – Layouts / App Layout (Desktop)

1. Create frame: 1440×900
2. Add 12-column grid (80px margins)
3. Place TopBar component at top
4. Place Sidebar (240px) on left
5. Place main content area (fill remaining)

### Page: 03 – Layouts / App Layout (Tablet)

1. Create frame: 1280×800
2. Add 12-column grid (64px margins)
3. Show responsive adjustments
4. Demonstrate how components adapt

### Page: 04 – Screens / Ask Query

1. Create full screen layout (desktop)
2. Place all components together
3. Show complete user interface
4. Add sample data and results

---

## ✅ Checklist

### Colors
- [ ] 4 Background colors created
- [ ] 4 Text colors created
- [ ] 3 Accent colors created
- [ ] 3 Risk colors created
- [ ] 2 Border colors created
- [ ] 1 Surface color created
- [ ] **Total: 17 color styles**

### Variables
- [ ] 3 Elevation tokens created (shadow effects)
- [ ] 6 Spacing variables created
- [ ] 3 Radius variables created
- [ ] 6 Typography variables created (optional)

### Layout
- [ ] 1440px desktop frame created
- [ ] 1280px tablet frame created
- [ ] 12-column grid added to both
- [ ] Desktop: 80px margins, 24px gutter
- [ ] Tablet: 64px margins, 24px gutter

### Components
- [ ] TopBar component created
- [ ] SidebarItem component with 4 variants (Default, Hover, Active, Disabled)
- [ ] QueryInput card component
- [ ] RiskBadge component with 3 variants (Safe, Warning, Danger)
- [ ] SQLPanel component
- [ ] Button component with 4 states (Default, Hover, Loading, Disabled)

### Component States
- [ ] SidebarItem: Default, Hover, Active, Disabled
- [ ] Button: Default, Hover, Loading, Disabled
- [ ] Input: Default, Focused, Filled, Disabled, Error
- [ ] All interactive components have loading states

### Organization
- [ ] 5 pages created (Foundations, Primitives, Components, Layouts, Screens)
- [ ] Components organized by category
- [ ] Color reference page created
- [ ] Elevation reference page created
- [ ] Layout examples created (desktop + tablet)
- [ ] Screen mockups created

---

## 🎯 Design Philosophy

### Controlled
- Consistent spacing (8pt system)
- Predictable colors
- Clear hierarchy

### Structured
- Organized file structure
- Named components
- Variant system

### Calm
- Muted color palette
- Soft rounded corners
- Minimal animations

### Transparent
- Clear naming conventions
- Documented tokens
- Reusable components

---

## 📝 Naming Conventions

### Colors
Format: `Category / Variant`
- `BG / Primary`
- `Text / Secondary`
- `Accent / Hover`
- `Risk / Danger`

### Components
Format: `Category / ComponentName`
- `Navigation / TopBar`
- `Card / QueryInput`
- `Status / RiskBadge`
- `Panel / SQLViewer`

### Variants
Format: `Property: Value`
- `State: Default`
- `State: Hover`
- `Level: Safe`

---

## 🚀 Next Steps

1. **Create all color styles** (16 total)
2. **Set up variables** (15 total)
3. **Configure layout grid** (12 columns)
4. **Build components** (5 main components)
5. **Organize pages** (5 pages)
6. **Create mockups** (3-4 screens)
7. **Share with team** (enable view access)

---

## 💡 Pro Tips

### Consistency
- Always use color styles (never manual colors)
- Always use variables (never hardcoded values)
- Always use components (never duplicate designs)

### Efficiency
- Create variants for all states
- Use auto layout for responsive design
- Name everything clearly

### Collaboration
- Share library with team
- Document all decisions
- Keep file organized

---

## 📚 Resources

- [Figma Color Styles Guide](https://help.figma.com/en/articles/360039820134)
- [Figma Variables Guide](https://help.figma.com/en/articles/15145231)
- [Figma Components Guide](https://help.figma.com/en/articles/360038662654)
- [Figma Auto Layout Guide](https://help.figma.com/en/articles/5731482)

---

## ✨ Result

After completing this setup, you'll have:

✅ **Professional design system**  
✅ **Reusable components**  
✅ **Consistent styling**  
✅ **Organized workspace**  
✅ **Team-ready library**  
✅ **Production-grade quality**  

---

**Status**: COMPLETE ✅  
**Ready for**: Design handoff  
**Quality**: Enterprise-grade  

