# Phase 2: Governance Chrome - Implementation Guide

**Date**: March 1, 2026  
**Status**: Ready to implement  
**Time**: 30 minutes  
**Goal**: Add governance overlays to query view

---

## 🎯 What We're Adding

### On Query View (Chat Component)
1. **Risk Score Badge** (prominent, next to send button)
   - 🟢 Green: <30 (Safe)
   - 🟠 Orange: 30-70 (Warning)
   - 🔴 Red: >70 (Danger)
   - Format: "🟢 18 | Safe"

2. **Validation Layers Indicator** (after execution)
   - "✓ SQL Validation passed"
   - "✓ Policy check passed"
   - "✓ Row limit applied (10,000)"
   - "✓ Execution time: 1.4s"

3. **Execution Summary Footer** (below results)
   - Validation layers passed
   - Row limit applied
   - Policy: Finance only
   - Time: 1.4s

4. **Editable SQL Toggle** (show original vs final)
   - "Original SQL" vs "Final SQL"
   - Show LIMIT → TOP rewrite
   - Show any policy-based modifications

---

## 📝 Implementation Steps

### Step 1: Create RiskBadge Component
**File**: `frontend/src/components/RiskBadge.tsx`

```typescript
interface RiskBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function RiskBadge({ score, size = 'md', showLabel = true }: RiskBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 70) return { color: '#DC2626', label: 'Danger', emoji: '🔴' };
    if (score >= 30) return { color: '#F59E0B', label: 'Warning', emoji: '🟠' };
    return { color: '#16A34A', label: 'Safe', emoji: '🟢' };
  };

  const { color, label, emoji } = getColor(score);

  return (
    <div className={`risk-badge risk-badge-${size}`} style={{ borderColor: color }}>
      <span className="risk-emoji">{emoji}</span>
      <span className="risk-score">{score}</span>
      {showLabel && <span className="risk-label">{label}</span>}
    </div>
  );
}
```

### Step 2: Create ValidationSummary Component
**File**: `frontend/src/components/ValidationSummary.tsx`

```typescript
interface ValidationSummaryProps {
  validationPassed: boolean;
  rowLimit?: number;
  policy?: string;
  executionTime?: number;
}

export function ValidationSummary({
  validationPassed,
  rowLimit,
  policy,
  executionTime
}: ValidationSummaryProps) {
  return (
    <div className="validation-summary">
      <div className="validation-item">
        <span className="check-icon">✓</span>
        <span>SQL Validation passed</span>
      </div>
      <div className="validation-item">
        <span className="check-icon">✓</span>
        <span>Policy check passed</span>
      </div>
      {rowLimit && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Row limit applied ({rowLimit.toLocaleString()})</span>
        </div>
      )}
      {policy && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Policy: {policy}</span>
        </div>
      )}
      {executionTime && (
        <div className="validation-item">
          <span className="check-icon">✓</span>
          <span>Execution time: {executionTime}ms</span>
        </div>
      )}
    </div>
  );
}
```

### Step 3: Update Chat Component
**File**: `frontend/src/components/Chat.tsx`

Add to input area (before send button):
```typescript
{/* Risk Score Badge */}
{riskScore !== null && (
  <RiskBadge score={riskScore} size="md" showLabel={true} />
)}
```

Add after results display:
```typescript
{/* Validation Summary */}
{msg.results && msg.results.length > 0 && (
  <ValidationSummary
    validationPassed={true}
    rowLimit={10000}
    policy="Finance only"
    executionTime={msg.executionTime}
  />
)}
```

### Step 4: Add SQL Toggle
**File**: `frontend/src/components/Chat.tsx`

Add state:
```typescript
const [showOriginalSQL, setShowOriginalSQL] = useState(false);
```

Add toggle button:
```typescript
{msg.sql && msg.finalSQL && msg.sql !== msg.finalSQL && (
  <div className="sql-toggle">
    <button
      onClick={() => setShowOriginalSQL(!showOriginalSQL)}
      className="toggle-btn"
    >
      {showOriginalSQL ? 'Show Final SQL' : 'Show Original SQL'}
    </button>
    <pre className="sql-display">
      {showOriginalSQL ? msg.sql : msg.finalSQL}
    </pre>
  </div>
)}
```

---

## 🎨 CSS Styling

### RiskBadge.css
```css
.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 2px solid;
  border-radius: 6px;
  background: var(--bg-elevated);
  font-size: 14px;
  font-weight: 600;
}

.risk-emoji {
  font-size: 16px;
}

.risk-score {
  font-weight: 700;
}

.risk-label {
  font-size: 12px;
  opacity: 0.8;
}
```

### ValidationSummary.css
```css
.validation-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-elevated);
  border-left: 3px solid var(--risk-safe);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.validation-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.check-icon {
  color: var(--risk-safe);
  font-weight: 700;
}
```

### SQL Toggle CSS
```css
.sql-toggle {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.toggle-btn {
  padding: 8px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.toggle-btn:hover {
  background: var(--bg-surface);
  border-color: var(--primary);
}

.sql-display {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  overflow-x: auto;
  color: var(--text-secondary);
}
```

---

## 📊 Data Flow

```
User asks question
    ↓
Backend processes
    ├─ Validates SQL
    ├─ Calculates risk score
    ├─ Checks policies
    └─ Executes query
    ↓
Response includes:
    ├─ results: []
    ├─ sql: "SELECT ..."
    ├─ finalSQL: "SELECT TOP 10 ..."
    ├─ riskScore: 18
    ├─ validationPassed: true
    ├─ executionTime: 245
    └─ policy: "Finance only"
    ↓
Frontend displays:
    ├─ Risk badge (🟢 18 | Safe)
    ├─ Results table
    ├─ Charts
    ├─ Validation summary
    └─ SQL toggle
```

---

## 🎯 Integration Points

### In Chat.tsx
1. Import RiskBadge and ValidationSummary
2. Add riskScore state
3. Add showOriginalSQL state
4. Render badge in input area
5. Render summary after results
6. Render SQL toggle

### In Chat.css
1. Add styles for risk badge
2. Add styles for validation summary
3. Add styles for SQL toggle

### In Message Display
1. Show risk badge next to send button
2. Show validation summary after results
3. Show SQL toggle for rewrites

---

## ✅ Verification Checklist

### Components
- [ ] RiskBadge renders correctly
- [ ] ValidationSummary renders correctly
- [ ] SQL toggle works
- [ ] All use CSS variables
- [ ] All are theme-aware

### Integration
- [ ] Badge shows in input area
- [ ] Summary shows after results
- [ ] Toggle shows for rewrites
- [ ] No TypeScript errors
- [ ] No console warnings

### Design
- [ ] Follows design system
- [ ] Proper spacing
- [ ] Smooth transitions
- [ ] Accessible
- [ ] Mobile responsive

---

## 🚀 Quick Start

1. Create RiskBadge component (10 min)
2. Create ValidationSummary component (10 min)
3. Update Chat component (5 min)
4. Add CSS styling (5 min)
5. Test and verify (5 min)

**Total**: 35 minutes

---

## 📈 Impact

### Before
- Query view looks like a chat interface
- No governance indicators
- User doesn't see risk scoring
- User doesn't see validation layers

### After
- Query view has governance chrome
- Risk score prominent
- Validation layers visible
- User sees: "Governance is built-in"
- Positioning: Reinforced

---

## 💡 Why This Matters

**Single UI change** (governance chrome) + **sidebar** = complete product repositioning

- Sidebar says: "This is a governance platform"
- Dashboard says: "Governance is the default"
- Query chrome says: "Governance is built-in"

**Result**: User mental model shifts from "query tool" to "governance control plane"

---

**Status**: Ready to implement  
**Time**: 30 minutes  
**Next**: Phase 3 - Dashboard Enhancement (45 min)  
**Total to Complete**: ~90 minutes
