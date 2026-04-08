# VoxQuery Composable Component Architecture

## Overview

The component system is organized into three tiers:

### 1. **UI Primitives** (`/components`)
Base building blocks with no domain knowledge.

- `Button` — CTA with optional size/variant
- `Input` — Text input field with label support
- `Card` — Container with border and padding
- `Badge` — Status label with color variants

### 2. **Layout Components** (`/components/layout`)
Establish consistent structure across pages.

- `Page` — Full-page wrapper with background (min-h-screen, dark theme)
- `Container` — Centered max-width wrapper (max-w-6xl, mx-auto)
- `Section` — Semantic block with padding (py-24)

### 3. **Domain Components** (`/components/voxcore`)
VoxCore-specific, reusable, data-driven UI.

- `RiskItem` — Single risk item (id, title, desc)
- `RiskScoreCard` — Color-coded risk score (score: number)
- `PolicyBlockCard` — Policy violation display (title, reason, policy)
- `AuditLogTable` — Table for audit entries (timestamp, user, action, result)
- `DemoFlow` — Step-by-step flow visualization (steps array)
- `ContextPanel` — Query context display (integrated in Playground)

---

## Usage Patterns

### Layout Pattern
```typescript
import { Page, Container, Section } from "@/components";

export const MyPage = () => {
  return (
    <Page>
      <Container>
        <Section>
          <h1>Page Title</h1>
        </Section>
        <Section>
          <p>More content</p>
        </Section>
      </Container>
    </Page>
  );
};
```

### Data-Driven Component Pattern
```typescript
import { RiskItem } from "@/components";

const risks = [
  { id: 1, title: "SQL Injection Risk", desc: "User input validation missing" },
  { id: 2, title: "Privilege Escalation", desc: "Admin endpoint exposed" },
];

export const RiskList = () => (
  <div className="space-y-4">
    {risks.map((risk) => (
      <RiskItem key={risk.id} {...risk} />
    ))}
  </div>
);
```

### Table Pattern
```typescript
import { AuditLogTable } from "@/components";

const entries = [
  {
    id: "1",
    timestamp: "2024-03-15 10:30",
    user: "alice@example.com",
    action: "SELECT * FROM users",
    result: "blocked" as const,
  },
];

export const AuditLog = () => <AuditLogTable entries={entries} />;
```

### Flow Pattern
```typescript
import { DemoFlow } from "@/components";

const steps = [
  { id: 1, title: "Connect Database", description: "Add your data source", completed: true },
  { id: 2, title: "Define Policies", description: "Set access rules", completed: false },
  { id: 3, title: "Run Queries", description: "Execute governed queries", completed: false },
];

export const Onboarding = () => <DemoFlow steps={steps} />;
```

---

## Component Export Structure

All components are exported from `/components/index.ts`:

```typescript
// UI Primitives
import { Button, Input, Card, Badge } from "@/components";

// Layout
import { Page, Container, Section } from "@/components";

// VoxCore Domain
import {
  RiskItem,
  RiskScoreCard,
  PolicyBlockCard,
  AuditLogTable,
  DemoFlow,
} from "@/components";
```

---

## Design Standards

### Styling
- **Color scheme:** Blue accents (#3B82F6), red warnings (#EF4444), green success (#10B981)
- **Dark theme:** Background #0B0F19, text white
- **Spacing:** Tailwind scale (py-2, py-4, py-6, py-24)
- **Borders:** Subtle white/10 or white/5 for dark theme

### TypeScript
- All components must have TypeScript interfaces
- Props interface naming: `ComponentNameProps`
- Use `as const` for string literal union types

### Accessibility
- Use semantic HTML (`<table>`, `<section>`, etc.)
- Include `key` prop when rendering lists
- Use proper heading hierarchy

---

## Refactoring Guide

### Before (Messy Manual JSX)
```typescript
export const SecurityPage = () => {
  return (
    <div style={{ background: "#0B0F19", padding: "20px" }}>
      <h1>Security</h1>
      <div style={{ marginTop: "40px" }}>
        <h2>Risk Assessment</h2>
        <div>
          <div>
            <span>Risk 1</span>
            <p>Description</p>
          </div>
          <div>
            <span>Risk 2</span>
            <p>Description</p>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### After (Composable System)
```typescript
import { Page, Container, Section, RiskItem } from "@/components";

const risks = [
  { id: 1, title: "Risk 1", desc: "Description" },
  { id: 2, title: "Risk 2", desc: "Description" },
];

export const SecurityPage = () => {
  return (
    <Page>
      <Container>
        <Section>
          <h1>Security</h1>
        </Section>
        <Section>
          <h2 className="mb-4">Risk Assessment</h2>
          <div className="space-y-4">
            {risks.map((risk) => (
              <RiskItem key={risk.id} {...risk} />
            ))}
          </div>
        </Section>
      </Container>
    </Page>
  );
};
```

---

## Quality Gates

All components enforce:
- ✅ Named exports only (`export const Component = ...`)
- ✅ TypeScript interfaces for props
- ✅ Proper JSX closing tags
- ✅ No inline onchange/onclick (extract to event handlers)
- ✅ ESLint strict rules (enforced on commit via Husky)

---

## Testing Pattern

Each component can be tested in isolation:

```typescript
// Test data
const mockRisks = [
  { id: 1, title: "Test Risk", desc: "Test Description" },
];

// Component test
render(
  <div className="space-y-4">
    {mockRisks.map((risk) => (
      <RiskItem key={risk.id} {...risk} />
    ))}
  </div>
);
```

---

## Integration Checklist

When refactoring an existing page:

- [ ] Replace inline styles with Tailwind classes
- [ ] Extract repeating JSX blocks to components
- [ ] Use `Page` → `Container` → `Section` hierarchy
- [ ] Convert loops to `.map()` with key props
- [ ] Add TypeScript interface for data structures
- [ ] Import all components from `@/components`
- [ ] Run `npm run lint:fix` to auto-format
- [ ] Run `npm run format` to verify Prettier compliance
- [ ] Test in browser to verify visual consistency

---

## Common Patterns Reference

| Pattern | Component | Example |
|---------|-----------|---------|
| List of items | RiskItem, AuditLogTable | Risk dashboard, activity log |
| Status display | Badge, RiskScoreCard | User roles, risk metrics |
| Form input | Input, Button | Login, settings form |
| Container | Page, Container, Section | Any page layout |
| Flow/steps | DemoFlow | Onboarding, wizard |
| Alerts | PolicyBlockCard | Policy violations, blocks |

---

## Next Steps

1. Refactor existing pages using composable system
2. Add unit tests for domain components
3. Create Storybook for component documentation
4. Document component variants (sizes, themes)
5. Build page templates for common layouts
