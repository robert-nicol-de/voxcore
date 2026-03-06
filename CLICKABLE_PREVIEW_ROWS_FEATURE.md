# Clickable Preview Rows Feature

## Overview
Made the "Previewing first 5 rows" text clickable to expand and view all rows in the results table.

## What Changed

### Frontend Updates

#### 1. Message Interface (`frontend/src/components/Chat.tsx`)
- Added `showAllRows?: boolean` property to Message interface
- Allows tracking whether to show all rows or just preview (first 5)

#### 2. Table Rendering Logic
- Updated table row slicing from fixed `.slice(0, 5)` to dynamic:
  ```typescript
  msg.results.slice(0, msg.showAllRows ? msg.results.length : 5)
  ```
- Now respects the `showAllRows` flag to show all rows when clicked

#### 3. Preview Text - Now Clickable
- Made "Previewing first 5 rows" text clickable
- Added click handler that toggles `showAllRows` state
- Text changes to "✓ Showing all rows" when expanded
- Added tooltip: "Click to view all rows"
- Styled with:
  - `cursor: pointer`
  - `color: var(--primary)` (blue)
  - `text-decoration: underline`

#### 4. CSS Styling (`frontend/src/components/Chat.css`)
- Updated `.more-rows` class with:
  - `cursor: pointer` - indicates clickability
  - `color: var(--primary)` - blue color to match links
  - `text-decoration: underline` - standard link styling
  - `transition: opacity 0.2s` - smooth hover effect
  - `user-select: none` - prevents text selection on click
  - `:hover` state with opacity change

## How It Works

### User Flow
1. Query returns more than 5 rows
2. Table shows first 5 rows only
3. Footer displays: "Previewing first 5 rows · Download Excel..."
4. User clicks on "Previewing first 5 rows" text
5. Table expands to show ALL rows
6. Text changes to "✓ Showing all rows"
7. User can click again to collapse back to 5 rows

### State Management
- `showAllRows` flag stored in message object
- Toggled via click handler in results footer
- Persists for the lifetime of the message
- Each message has independent state

## Visual Indicators
- **Before Click**: "Previewing first 5 rows" (blue, underlined, cursor pointer)
- **After Click**: "✓ Showing all rows" (blue, underlined)
- **Hover**: Slight opacity change for feedback

## Benefits
- ✅ Users can preview results quickly (first 5 rows)
- ✅ Users can expand to see full dataset without downloading
- ✅ Clear visual indication that text is clickable
- ✅ Smooth toggle between preview and full view
- ✅ Download Excel still available for export

## Files Modified
1. `frontend/src/components/Chat.tsx` - Added showAllRows property and click handler
2. `frontend/src/components/Chat.css` - Updated .more-rows styling for interactivity

## Testing
- ✅ Click "Previewing first 5 rows" to expand
- ✅ Text changes to "✓ Showing all rows"
- ✅ All rows now visible in table
- ✅ Click again to collapse back to 5 rows
- ✅ Hover shows visual feedback
- ✅ Works with all result sets > 5 rows

