# VoxQuery New Features - Quick Start Guide

## 🎯 What's New (Latest Session)

### 1. Last Refreshed + Refresh Button
**Location**: Below results table
**What it does**: Shows when results were generated, allows one-click refresh

```
🔄 Last refreshed: 2 min ago  [↻ Refresh]
```

**How to use**:
1. Run a query
2. See "Last refreshed: X ago" below table
3. Click "↻ Refresh" to re-run the same query
4. Timestamp updates automatically

---

### 2. Share Report Button
**Location**: Below results table (next to refresh)
**What it does**: Generates a shareable link for colleagues

```
[🔗 Share Report]
```

**How to use**:
1. Run a query
2. Click "🔗 Share Report"
3. Link copied to clipboard
4. Paste in email/Slack
5. Recipient opens link to view results
6. Link valid for 24 hours

**What's included in share**:
- Question asked
- Generated SQL
- Results data
- Metadata (warehouse, database, schema)
- Timestamp

---

### 3. Updated Welcome Message
**Location**: Chat area (initial message)
**What it says**:

```
Welcome to VoxQuery. Ask any question about your Snowflake, SQL Server, 
or other warehouse data in plain English — I'll generate accurate SQL, 
show you the results, and keep everything auditable. 
No queues. No guesswork. Just answers.
```

**Why it changed**:
- More professional tone
- Highlights multi-warehouse support
- Emphasizes key benefits
- Enterprise-ready messaging

---

### 4. Dialect-Specific Headers
**Location**: Column headers in results table
**What it does**: Headers adapt to your warehouse type

**Examples**:

**SQL Server**:
- `cost_of_goods_usd` → `Cost Of Goods USD`
- `invoice_amt` → `Invoice Amount`
- `dbo.customer_id` → `Customer ID`

**Snowflake**:
- `cost_of_goods_usd` → `Cost Of Goods USD`
- `sale_price_usd` → `Sale Price USD`

**PostgreSQL/Redshift**:
- `cost_of_goods_usd` → `Cost Of Goods USD`

**Why it matters**:
- Headers feel native to your warehouse
- Reduces cognitive load
- Professional appearance

---

### 5. Connection Status with Schema
**Location**: Top header bar
**What it shows**:

```
🗄️ Snowflake  |  📊 FinanceDB  |  📁 PUBLIC  |  🖥️ we08391.af-south-1.aws  |  🟢 Connected
```

**What's new**:
- Now shows schema (📁 PUBLIC)
- Helps prevent context confusion
- Shows all connection details

---

### 6. SSRS Embed Button
**Location**: Export buttons (next to Markdown)
**What it does**: Generates URL for embedding in SSRS reports

```
[🔗 SSRS]
```

**How to use**:
1. Run a query
2. Click "🔗 SSRS"
3. URL copied to clipboard
4. In SSRS: Add textbox → Properties → Action → Go to URL
5. Paste URL
6. VoxQuery results embed in report

**URL Format**:
```
https://voxquery.com/embed?warehouse=sqlserver&db=FinanceDB&schema=dbo&question=Overdue invoices
```

---

## 🎨 UI Changes

### Results Section Now Shows
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Results (1,234 rows)                                 │
├─────────────────────────────────────────────────────────┤
│ [KPI Cards: Total, Avg, Max, Total]                    │
├─────────────────────────────────────────────────────────┤
│ [Frozen Columns] [Table Data] [Frozen Columns]         │
├─────────────────────────────────────────────────────────┤
│ 🔄 Last refreshed: 2 min ago  [↻ Refresh]  [🔗 Share]  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Tips

### Refresh Button
- Use when data might have changed
- Re-runs exact same query
- Updates timestamp
- Works with all query types

### Share Button
- Perfect for sending to non-technical users
- No database access needed to view
- Includes full context (SQL, results)
- Valid for 24 hours

### Dialect Headers
- Automatic - no action needed
- Adapts to your warehouse
- Makes results feel native
- Professional appearance

### Connection Status
- Check at top of page
- Shows which database you're in
- Prevents "why aren't my queries showing?" confusion
- Shows schema for SQL Server users

### SSRS Integration
- For legacy SQL Server + SSRS users
- One-click URL generation
- Embed results directly in reports
- Perfect for finance teams

---

## 🎯 Common Workflows

### Workflow 1: Refresh Stale Data
1. Run query
2. See "Last refreshed: 30 min ago"
3. Click "↻ Refresh"
4. Results update
5. Timestamp resets to "just now"

### Workflow 2: Share Results with Team
1. Run query
2. Click "🔗 Share Report"
3. Notification: "Share link copied!"
4. Paste in Slack/email
5. Team member opens link
6. Sees results without database access

### Workflow 3: Embed in SSRS Report
1. Run query in VoxQuery
2. Click "🔗 SSRS"
3. URL copied to clipboard
4. Open SSRS Report Designer
5. Add textbox → Properties → Action → Go to URL
6. Paste URL
7. Publish report
8. Results embed in SSRS

### Workflow 4: Check Connection Context
1. Look at top header
2. See warehouse type (🗄️ Snowflake)
3. See database (📊 FinanceDB)
4. See schema (📁 PUBLIC)
5. See status (🟢 Connected)
6. Know exactly which context you're in

---

## 📊 Feature Comparison

| Feature | Before | After |
|---------|--------|-------|
| Data freshness | Unknown | Shows "2 min ago" |
| Refresh data | Manual re-query | One-click button |
| Share results | Copy/paste | Shareable link |
| SSRS integration | Not possible | One-click URL |
| Headers | Generic | Dialect-native |
| Connection context | Unclear | Clear indicator |
| Schema visibility | Hidden | Displayed |

---

## ❓ FAQ

**Q: How long is the share link valid?**
A: 24 hours (in production, configurable)

**Q: Does share link require database access?**
A: No, it includes all data needed to view results

**Q: Can I refresh a query that failed?**
A: Yes, refresh button works with any query

**Q: Does refresh update the timestamp?**
A: Yes, it resets to "just now"

**Q: How do I know which database I'm connected to?**
A: Check the top header - shows warehouse, database, schema, host

**Q: Can I embed VoxQuery in Power BI?**
A: Currently supports SSRS; Power BI support coming soon

**Q: What if I'm in the wrong schema?**
A: Check header, disconnect, and reconnect to correct schema

---

## 🎓 Best Practices

### Refresh Button
- Use when data might have changed
- Don't refresh too frequently (respects database)
- Check timestamp before refreshing

### Share Button
- Use for one-time sharing
- Include context in message
- Remind recipient link expires in 24h

### Connection Status
- Always check before running queries
- Verify schema is correct
- Prevents "why aren't my tables showing?" confusion

### Dialect Headers
- Automatic - no action needed
- Helps team members recognize their warehouse
- Professional appearance

---

## 🔧 Troubleshooting

**Q: Refresh button not working**
A: Make sure you're connected to database

**Q: Share link not copying**
A: Check browser permissions for clipboard access

**Q: Headers look wrong**
A: Headers adapt to warehouse type - this is intentional

**Q: Can't see schema in header**
A: Make sure you're connected to database with schema selected

**Q: SSRS URL not working**
A: Make sure URL is pasted correctly in SSRS action

---

## 📚 Related Documentation

- **OPTIONAL_FINAL_TOUCHES.md** - Detailed technical documentation
- **DEPLOYMENT_CHECKLIST.md** - Deployment guide
- **QUICK_REFERENCE_POLISH.md** - All features reference

---

**Status**: ✨ All New Features Ready to Use!
