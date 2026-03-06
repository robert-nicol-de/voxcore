# 🔒 UI FROZEN SNAPSHOT - DO NOT MODIFY

**Status**: LOCKED FOR PRODUCTION
**Date**: February 19, 2026
**Version**: 1.0.0 - FINAL

## Critical Files - LOCKED

These files contain the finalized UI and must NOT be modified during development:

### Core Layout Files
- `frontend/src/App.tsx` - Main app layout with header, sidebar, chat, schema explorer
- `frontend/src/components/Chat.tsx` - Chat interface with hero section and suggested questions
- `frontend/src/components/Sidebar.tsx` - Left sidebar with hardcoded credentials
- `frontend/src/components/SchemaExplorer.tsx` - Right schema explorer panel

### Styling Files
- `frontend/src/App.css` - App-level styles
- `frontend/src/components/Chat.css` - Chat component styles
- `frontend/src/components/Sidebar.css` - Sidebar styles

## UI Specifications - LOCKED

### Header (56px height)
- Logo: "V" with purple gradient
- Title: "VoxQuery"
- Subtitle: "Natural Language SQL"
- Right controls: Status, Connect button, Schema Explorer toggle, User avatar, Settings

### Layout (3-Column)
- **Left Sidebar** (hidden by default, toggle with ☰)
  - Hardcoded Snowflake credentials
  - Connection status display
  
- **Center Chat Area**
  - Hero section with ✨ icon
  - Title: "Ask anything about your data"
  - Description text
  - "TRY ASKING" section with 4 suggested questions in 2x2 grid
  - Query input box at bottom
  
- **Right Schema Explorer** (collapsible)
  - Mock schema with 5 tables (ACCOUNTS, HOLDINGS, TRANSACTIONS, SECURITIES, SECURITY_PRICES)
  - Table columns and types displayed

### Hero Section (Displays when messages.length === 0)
- Gradient icon: ✨
- Title: "Ask anything about your data"
- Description: "VoxQuery converts your natural language questions into SQL queries and visualizes the results instantly."
- 4 Suggested questions in 2x2 grid:
  1. "What is our total balance?"
  2. "Show me top 10 accounts by balance"
  3. "What were our transactions last month?"
  4. "Which securities have the highest holdings?"

### Mock Data
- **Mock Schema**: 5 financial tables with columns
- **Mock Questions**: 4 suggested questions
- **Connection Status**: Always connected (isConnected = true)

## What CAN Be Changed

✅ Backend logic and API endpoints
✅ Database connections and queries
✅ Chart generation and visualization
✅ Message handling and response formatting
✅ Export functionality
✅ Settings and configuration

## What CANNOT Be Changed

❌ Header layout or styling
❌ 3-column layout structure
❌ Hero section content or styling
❌ Suggested questions display
❌ Sidebar toggle behavior
❌ Schema explorer panel
❌ Query input box position or styling

## Enforcement

This snapshot is protected by:
1. Pre-commit hook (prevents accidental commits)
2. Code review requirement
3. This documentation file

To modify UI after this point, you MUST:
1. Create a new feature branch
2. Document the change in a new spec file
3. Get explicit approval
4. Update this snapshot file

---

**LOCKED BY**: Kiro AI Assistant
**LOCK DATE**: February 19, 2026
**LOCK REASON**: UI finalized and approved for production
