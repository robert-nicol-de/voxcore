# VoxCore Figma Design System - 5-Page Structure

**Status**: Ready for Figma Implementation  
**Date**: February 28, 2026  
**Quality**: Enterprise-grade

---

## FIGMA FILE SETUP

### File Name
`VoxCore Platform - Design System v1.0`

### File Settings
- **Color Mode**: Dark (RGB)
- **Units**: Pixels
- **Grid**: 8px
- **Guides**: Enabled

---

## PAGE STRUCTURE (5 Pages)

### PAGE 1: OVERVIEW

**Purpose**: Landing page for design system  
**Audience**: Designers, PMs, stakeholders

**Contents**:
- Brand story (VoxCore Platform)
- Design principles (Controlled, Structured, Calm, Transparent)
- Component count (15+ components)
- Color palette preview (17 colors)
- Typography scale
- Spacing system
- Shadow system
- Usage guidelines

**Layout**:
- Hero section (brand story)
- 4 principle cards (Controlled, Structured, Calm, Transparent)
- Color palette grid (17 colors with hex codes)
- Typography scale (H1-H6, Body, Caption)
- Spacing tokens (8pt system)
- Shadow examples (3 levels)
- Quick links to other pages

---

### PAGE 2: PRIMITIVES

**Purpose**: Atomic building blocks  
**Audience**: Developers, designers

**Contents**:

#### Buttons (All States)
- Primary button
  - Default
  - Hover
  - Loading
  - Disabled
- Secondary button
  - Default
  - Hover
  - Disabled

#### Inputs (All States)
- Text input
  - Default
  - Focused
  - Filled
  - Disabled
  - Error
- Checkbox
  - Unchecked
  - Checked
  - Disabled
- Radio
  - Unselected
  - Selected
  - Disabled
- Toggle/Switch
  - Off
  - On
  - Disabled

#### Badges
- Safe (green)
- Warning (yellow)
- Danger (red)
- Info (blue)

#### Other Primitives
- Labels
- Help text
- Icons (16px, 24px, 32px)
- Dividers
- Spacers

**Layout**:
- Grid layout (4 columns)
- Each component with all states
- Annotations for states
- Spacing guides

---

### PAGE 3: COMPOSITE

**Purpose**: Combinations of primitives  
**Audience**: Developers, designers

**Contents**:

#### Cards
- Metric card (number + label + trend)
- Status card (icon + status + description)
- Data card (title + content)

#### Panels
- Side panel (navigation)
- Modal panel (dialog)
- Floating panel (popover)

#### Navigation
- Sidebar (with active state)
- Top navigation bar
- Breadcrumbs

#### Forms
- Form group (label + input + help text)
- Form section (multiple groups)
- Form with validation

#### Alerts
- Alert box (warning, error, info, success)
- Toast notification
- Inline alert

#### Tables
- Table header
- Table row (default, hover, selected)
- Table with sorting
- Table with pagination

**Layout**:
- Component showcase (each component with variations)
- Annotations for interactions
- State documentation

---

### PAGE 4: LAYOUTS

**Purpose**: Full-page layouts  
**Audience**: Developers, designers

**Contents**:

#### Dashboard Layout
- Header (56px)
- Sidebar (280px)
- Content area
- Grid layout (4 columns)
- Metric cards
- Charts
- Tables

#### Query Executor Layout
- Header
- Sidebar
- Query input area
- SQL display
- Results table
- Charts

#### Admin Layout
- Header
- Sidebar
- Form area
- Policy toggles
- Configuration panels

#### Login Layout
- Centered form
- Logo
- Input fields
- Button
- Help text

#### Error Layout
- Centered error message
- Icon
- Description
- Action button

**Layout**:
- Desktop (1920px)
- Tablet (1280px)
- Mobile (375px)
- Responsive annotations

---

### PAGE 5: USAGE GUIDE

**Purpose**: Implementation reference  
**Audience**: Developers

**Contents**:

#### Component API
- Button
  - Props: variant, state, onClick, className
  - States: default, hover, loading, disabled
  - Example usage
- Input
  - Props: value, onChange, placeholder, state, errorMessage
  - States: default, focused, filled, disabled, error
  - Example usage
- Card
  - Props: children, elevation, className
  - Elevations: sm, md, lg
  - Example usage
- Badge
  - Props: children, variant
  - Variants: safe, warning, danger, info
  - Example usage
- Layout
  - Props: children, sidebar, header
  - Example usage

#### Code Examples
- React component usage
- CSS variable usage
- Responsive implementation
- Accessibility notes

#### Do's and Don'ts
- Button usage
- Input validation
- Color usage
- Spacing guidelines

#### Performance Tips
- Component optimization
- Bundle size
- Lazy loading
- Caching

#### Accessibility
- WCAG AAA compliance
- Keyboard navigation
- Screen reader support
- Color contrast

---

## DESIGN TOKENS IN FIGMA

### Color Styles (17 Colors)

**Neutrals**:
- Background: #0F172A
- Surface: #1A202C
- Surface/Elevated: #1E293B
- Border: #334155
- Text Secondary: #64748B
- Text Primary: #F1F5F9

**Semantic**:
- Success: #10B981
- Warning: #F59E0B
- Error: #EF4444
- Info: #3B82F6
- Accent Primary: #6366F1
- Brand: #7C3AED

**Status**:
- Passed: #10B981
- Rewritten: #F59E0B
- Blocked: #EF4444

### Typography Styles

**Headings**:
- H1: 32px, 600 weight, line-height 1.2
- H2: 28px, 600 weight, line-height 1.2
- H3: 24px, 600 weight, line-height 1.3
- H4: 20px, 600 weight, line-height 1.3
- H5: 16px, 600 weight, line-height 1.4
- H6: 14px, 600 weight, line-height 1.4

**Body**:
- Body Large: 16px, 400 weight, line-height 1.5
- Body: 15px, 400 weight, line-height 1.5
- Body Small: 14px, 400 weight, line-height 1.5

**Captions**:
- Caption: 13px, 400 weight, line-height 1.4
- Overline: 12px, 600 weight, line-height 1.4

### Shadow Styles

- Shadow SM: 0 4px 16px rgba(0, 0, 0, 0.12)
- Shadow MD: 0 8px 24px rgba(0, 0, 0, 0.16)
- Shadow LG: 0 12px 32px rgba(0, 0, 0, 0.20)

### Spacing Tokens

- Spacing 1: 8px
- Spacing 2: 16px
- Spacing 3: 24px
- Spacing 4: 32px
- Spacing 5: 48px
- Spacing 6: 64px

### Border Radius

- Radius SM: 8px
- Radius MD: 12px
- Radius LG: 16px

---

## COMPONENT SPECIFICATIONS

### Button Component

**Variants**:
- Primary
- Secondary

**States**:
- Default
- Hover
- Loading
- Disabled

**Specs**:
- Padding: 16px 24px
- Border Radius: 12px
- Font Size: 15px
- Font Weight: 500
- Transition: 200ms ease-in-out

### Input Component

**States**:
- Default
- Focused
- Filled
- Disabled
- Error

**Specs**:
- Padding: 16px 24px
- Border Radius: 12px
- Font Size: 15px
- Border: 1px solid
- Transition: 200ms ease-in-out

### Card Component

**Elevations**:
- SM: Shadow SM
- MD: Shadow MD
- LG: Shadow LG

**Specs**:
- Padding: 24px
- Border Radius: 12px
- Border: 1px solid Border color
- Background: Surface color

### Badge Component

**Variants**:
- Safe (Green)
- Warning (Yellow)
- Danger (Red)
- Info (Blue)

**Specs**:
- Padding: 8px 16px
- Border Radius: 8px
- Font Size: 13px
- Font Weight: 600

---

## RESPONSIVE BREAKPOINTS

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
- Sidebar: Overlay/Drawer
- Header: 48px

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Setup (Day 1)
- [ ] Create Figma file
- [ ] Set up color styles (17 colors)
- [ ] Set up typography styles
- [ ] Set up shadow styles
- [ ] Create 5 pages

### Phase 2: Primitives (Days 2-3)
- [ ] Button component (all states)
- [ ] Input component (all states)
- [ ] Badge component (all variants)
- [ ] Other primitives (checkbox, radio, toggle)

### Phase 3: Composite (Days 4-5)
- [ ] Card components
- [ ] Navigation components
- [ ] Form components
- [ ] Alert components
- [ ] Table components

### Phase 4: Layouts (Days 6-7)
- [ ] Dashboard layout
- [ ] Query executor layout
- [ ] Admin layout
- [ ] Responsive variants

### Phase 5: Documentation (Days 8-10)
- [ ] Component API documentation
- [ ] Code examples
- [ ] Do's and don'ts
- [ ] Accessibility notes
- [ ] Performance tips

---

## FIGMA PLUGINS RECOMMENDED

- **Design Tokens**: Sync tokens to code
- **Figma to Code**: Export components as React
- **Accessibility Checker**: WCAG compliance
- **Contrast**: Color contrast validation
- **Measure**: Spacing and sizing

---

## NEXT STEPS

1. Create Figma file with 5-page structure
2. Set up all design tokens (colors, typography, shadows)
3. Build primitive components (Button, Input, Badge)
4. Build composite components (Card, Modal, Navigation)
5. Create layout templates
6. Document all components
7. Export components as React code
8. Sync tokens to frontend codebase

---

**Status**: Ready for Figma Implementation  
**Quality**: Enterprise-grade  
**Effort**: 10 working days

