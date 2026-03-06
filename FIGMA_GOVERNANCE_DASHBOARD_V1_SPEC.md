# Figma: Governance Dashboard V1 Specification

**Date**: February 28, 2026  
**Status**: Ready for Figma Implementation  
**Scope**: Design only (do NOT touch Query screen)

---

## 📐 Canvas Setup

**Frame Name**: `Screen / Governance Dashboard V1`  
**Frame Size**: 1920 × 1080 (Desktop)  
**Background**: `Color/Background` (#0F172A)  
**Padding**: 32px all sides  
**Grid**: 8pt (from design system)

---

## 🎯 Layout Structure (4 Rows)

```
┌─────────────────────────────────────────────────────────────┐
│ ROW 1: 4 KPI Cards (1 row, 4 columns)                       │
├─────────────────────────────────────────────────────────────┤
│ ROW 2: Governance Health Bar (full width)                   │
├─────────────────────────────────────────────────────────────┤
│ ROW 3: Alerts + Activity (2 columns)                        │
├─────────────────────────────────────────────────────────────┤
│ ROW 4: Risk Trends (full width)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 ROW 1: KPI Cards (4 Cards)

**Layout**: 4 equal columns, 24px gap between cards  
**Card Size**: 400 × 200px each  
**Component**: Use existing `Card` component

### Card 1: Total Queries
- **Title**: "Total Queries" (Typography/Label-Small, Color/Text-Secondary)
- **Value**: "2,847" (Typography/Display-Large, Color/Text-Primary)
- **Subtitle**: "+12% from last week" (Typography/Caption, Color/Success)
- **Icon**: Query icon (24×24, Color/Primary)
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)

### Card 2: Risk Score
- **Title**: "Avg Risk Score" (Typography/Label-Small, Color/Text-Secondary)
- **Value**: "24" (Typography/Display-Large, Color/Text-Primary)
- **Subtitle**: "Safe" (Typography/Caption, Color/Success)
- **Icon**: Shield icon (24×24, Color/Success)
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)

### Card 3: Blocked Queries
- **Title**: "Blocked Queries" (Typography/Label-Small, Color/Text-Secondary)
- **Value**: "18" (Typography/Display-Large, Color/Text-Primary)
- **Subtitle**: "Destructive operations" (Typography/Caption, Color/Warning)
- **Icon**: Block icon (24×24, Color/Warning)
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)

### Card 4: Compliance Rate
- **Title**: "Compliance Rate" (Typography/Label-Small, Color/Text-Secondary)
- **Value**: "99.2%" (Typography/Display-Large, Color/Text-Primary)
- **Subtitle**: "Policy adherence" (Typography/Caption, Color/Success)
- **Icon**: Check icon (24×24, Color/Success)
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)

---

## 📈 ROW 2: Governance Health Bar

**Layout**: Full width (1856px)  
**Height**: 120px  
**Component**: Custom component (not in library yet)

### Structure:
```
┌─ Health Status ─────────────────────────────────────────┐
│ Title: "Governance Health"                              │
│ Subtitle: "System status across all policies"           │
│                                                          │
│ [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] │
│  92% Healthy                                             │
│                                                          │
│ Status Indicators:                                       │
│ ✓ SQL Validation: Active  | ✓ Risk Scoring: Active     │
│ ✓ Execution Logging: Active | ✓ Policies: Enforced     │
└─────────────────────────────────────────────────────────┘
```

### Details:
- **Background**: `Color/Surface/Elevated` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)
- **Padding**: 24px
- **Title**: Typography/Heading-3, Color/Text-Primary
- **Subtitle**: Typography/Body-Small, Color/Text-Secondary
- **Progress Bar**: 
  - Background: `Color/Background` (#0F172A)
  - Fill: `Color/Success` (#10B981)
  - Height: 8px
  - Border-radius: 4px
- **Status Indicators**: 4 items, Typography/Caption, Color/Success

---

## 🚨 ROW 3: Alerts + Activity (2 Columns)

**Layout**: 2 equal columns, 24px gap  
**Height**: 300px each

### Column 1: Recent Alerts

**Component**: Custom (Card-based)  
**Size**: 896 × 300px

```
┌─ Recent Alerts ─────────────────────────────────────┐
│ Title: "Recent Alerts"                              │
│ Subtitle: "Last 24 hours"                           │
│                                                      │
│ [Alert 1] ⚠️ High Risk Query Detected               │
│           User: john@company.com                    │
│           Time: 2 hours ago                         │
│           Risk: 78 (Danger)                         │
│                                                      │
│ [Alert 2] 🚫 Destructive Operation Blocked          │
│           User: jane@company.com                    │
│           Time: 4 hours ago                         │
│           Operation: DELETE                        │
│                                                      │
│ [Alert 3] ✓ Policy Update Applied                   │
│           Admin: admin@company.com                  │
│           Time: 6 hours ago                         │
│           Policies: 3 updated                       │
│                                                      │
│ [View All Alerts →]                                 │
└─────────────────────────────────────────────────────┘
```

**Styling**:
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)
- **Padding**: 24px
- **Title**: Typography/Heading-3, Color/Text-Primary
- **Subtitle**: Typography/Caption, Color/Text-Secondary
- **Alert Items**: 
  - Padding: 16px
  - Border-bottom: 1px `Color/Border` (#334155)
  - Icon: 20×20, colored by severity
  - Text: Typography/Body-Small
  - Timestamp: Typography/Caption, Color/Text-Secondary

### Column 2: Activity Feed

**Component**: Custom (Card-based)  
**Size**: 896 × 300px

```
┌─ Activity Feed ─────────────────────────────────────┐
│ Title: "Activity Feed"                              │
│ Subtitle: "Real-time governance events"             │
│                                                      │
│ [Activity 1] Query Executed                         │
│              john@company.com                       │
│              SELECT * FROM ACCOUNTS                 │
│              Risk: 12 (Safe) | 2 hours ago          │
│                                                      │
│ [Activity 2] Policy Enforced                        │
│              System                                 │
│              Blocked: DELETE operation              │
│              Risk: 95 (Danger) | 3 hours ago        │
│                                                      │
│ [Activity 3] Schema Analyzed                        │
│              System                                 │
│              Tables: 12 | Columns: 156              │
│              Risk: 8 (Safe) | 5 hours ago           │
│                                                      │
│ [View All Activity →]                               │
└─────────────────────────────────────────────────────┘
```

**Styling**:
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)
- **Padding**: 24px
- **Title**: Typography/Heading-3, Color/Text-Primary
- **Subtitle**: Typography/Caption, Color/Text-Secondary
- **Activity Items**:
  - Padding: 16px
  - Border-bottom: 1px `Color/Border` (#334155)
  - Icon: 20×20, colored by action type
  - Text: Typography/Body-Small
  - Timestamp: Typography/Caption, Color/Text-Secondary

---

## 📉 ROW 4: Risk Trends

**Layout**: Full width (1856px)  
**Height**: 300px  
**Component**: Custom (Chart-based)

```
┌─ Risk Trends (Last 7 Days) ─────────────────────────┐
│ Title: "Risk Trends"                                │
│ Subtitle: "Query risk distribution over time"       │
│                                                      │
│ 100 │                                               │
│  80 │     ╱╲                                         │
│  60 │    ╱  ╲      ╱╲                               │
│  40 │   ╱    ╲    ╱  ╲    ╱╲                        │
│  20 │  ╱      ╲  ╱    ╲  ╱  ╲                       │
│   0 │_╱________╲╱______╲╱____╲_                     │
│     └─────────────────────────────                  │
│     Mon Tue Wed Thu Fri Sat Sun                     │
│                                                      │
│ Legend:                                              │
│ ─── Safe (0-30)  ─── Warning (31-70)  ─── Danger (71-100) │
└─────────────────────────────────────────────────────┘
```

**Styling**:
- **Background**: `Color/Surface` (#1E293B)
- **Border**: 1px `Color/Border` (#334155)
- **Padding**: 24px
- **Title**: Typography/Heading-3, Color/Text-Primary
- **Subtitle**: Typography/Caption, Color/Text-Secondary
- **Chart Area**: 
  - Background: `Color/Background` (#0F172A)
  - Border-radius: 8px
  - Padding: 16px
- **Lines**:
  - Safe: `Color/Success` (#10B981), 2px
  - Warning: `Color/Warning` (#F59E0B), 2px
  - Danger: `Color/Danger` (#EF4444), 2px
- **Axis Labels**: Typography/Caption, Color/Text-Secondary
- **Legend**: Typography/Caption, Color/Text-Secondary

---

## 🎨 Design System References

### Colors Used
- `Color/Background`: #0F172A
- `Color/Surface`: #1E293B
- `Color/Surface/Elevated`: #1E293B
- `Color/Border`: #334155
- `Color/Text-Primary`: #F1F5F9
- `Color/Text-Secondary`: #94A3B8
- `Color/Success`: #10B981
- `Color/Warning`: #F59E0B
- `Color/Danger`: #EF4444
- `Color/Primary`: #3B82F6

### Typography Used
- **Display-Large**: 32px, 700 weight, line-height 40px
- **Heading-3**: 20px, 600 weight, line-height 28px
- **Body-Small**: 14px, 400 weight, line-height 20px
- **Label-Small**: 12px, 600 weight, line-height 16px
- **Caption**: 12px, 400 weight, line-height 16px

### Spacing Used
- **Gap between cards**: 24px
- **Card padding**: 24px
- **Item padding**: 16px
- **Frame padding**: 32px
- **Grid**: 8pt

### Shadows Used
- **Elevation/1**: 0 4px 16px rgba(0,0,0,0.12)
- **Elevation/2**: 0 8px 24px rgba(0,0,0,0.16)
- **Elevation/3**: 0 12px 32px rgba(0,0,0,0.20)

---

## 🔧 Implementation Steps in Figma

1. **Create Frame**: 1920 × 1080, name "Screen / Governance Dashboard V1"
2. **Set Background**: #0F172A
3. **Add Padding**: 32px all sides
4. **Row 1**: Create 4 KPI cards using Card component
5. **Row 2**: Create Governance Health bar (custom)
6. **Row 3**: Create 2-column layout with Alerts + Activity
7. **Row 4**: Create Risk Trends chart (custom)
8. **Apply Spacing**: 24px between rows
9. **Use Design Tokens**: All colors, typography, shadows from design system
10. **Create Variants**: For each component (hover, active, disabled states)

---

## ✅ Checklist

- [ ] Frame created with correct dimensions
- [ ] Background color applied
- [ ] Padding and grid set up
- [ ] Row 1: 4 KPI cards created
- [ ] Row 2: Governance Health bar created
- [ ] Row 3: Alerts column created
- [ ] Row 3: Activity Feed column created
- [ ] Row 4: Risk Trends chart created
- [ ] All colors from design system applied
- [ ] All typography from design system applied
- [ ] All spacing from design system applied
- [ ] Component variants created (hover, active, disabled)
- [ ] Responsive breakpoints considered (tablet, mobile)
- [ ] Ready for handoff to React implementation

---

## 📝 Notes

- **Do NOT touch the Query screen** - focus only on Governance Dashboard
- Use existing Card component from design system
- Use existing Risk Badge component for risk indicators
- All custom components (Health Bar, Alerts, Activity, Trends) should follow the design system patterns
- Maintain 8pt grid throughout
- Use design tokens consistently
- Create component variants for all interactive states

---

**Status**: Ready for Figma  
**Next**: Open Figma and create the screen using this specification

