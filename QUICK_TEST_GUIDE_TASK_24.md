# Quick Test Guide - Task 24

## What Changed

### Frontend
- Added CSS for 2×2 chart grid layout
- Grid displays 4 equal cells: BAR, PIE, LINE, COMPARISON
- Each cell has label bar and chart content area
- Click any cell to enlarge chart in modal

### Backend
- Improved SQL generation prompt to prevent SELECT 1
- Added explicit warning about SELECT 1 being invalid
- Better fallback logic for invalid LLM outputs

## How to Test

### 1. Start Frontend
```bash
cd frontend
npm run dev
```

### 2. Start Backend
```bash
cd backend
python main.py
```

### 3. Test Chart Grid Display
1. Connect to database
2. Ask a question: "Show me the top 10 records"
3. Verify:
   - ✅ Results display below query
   - ✅ 4 KPI cards show (Total Rows, Avg, Max, Total)
   - ✅ 2×2 chart grid appears below KPI cards
   - ✅ Grid has 4 equal-sized cells
   - ✅ Each cell has label (BAR, PIE, LINE, COMPARISON)
   - ✅ Each cell shows chart preview
   - ✅ Cells have hover effects (border color, shadow, lift)

### 4. Test Click-to-Enlarge
1. Click any chart cell
2. Verify:
   - ✅ Modal overlay appears
   - ✅ Chart enlarges to full size
   - ✅ Close button (×) appears in top-right
   - ✅ Click close button to dismiss modal
   - ✅ Click outside modal to dismiss

### 5. Test SQL Generation
1. Ask: "Show me the top 10 records"
2. Check backend logs for:
   - ✅ "Schema context loaded: X chars"
   - ✅ "Raw LLM output: SELECT ..." (should be real SQL, not SELECT 1)
   - ✅ "Final SQL: SELECT ..." (should be valid query)

### 6. Test Light/Dark Theme
1. Toggle theme in settings
2. Verify:
   - ✅ Chart grid colors adjust properly
   - ✅ Labels remain readable
   - ✅ Hover effects work in both themes

## Expected Behavior

### Chart Grid
- 2 columns, 2 rows
- 16px gap between cells
- 380px total height
- Each cell: 190px height
- Label bar: dark background, white text, uppercase
- Content area: shows chart preview or "No data" message

### SQL Generation
- Real SQL queries (not SELECT 1)
- Proper T-SQL syntax for SQL Server
- Schema context properly injected
- Fallback queries if LLM fails

## Troubleshooting

### Charts not displaying
- Check browser console for errors
- Verify iframe rendering is working
- Check if msg.chart contains valid HTML

### Grid layout wrong
- Check CSS media queries
- Verify grid-template-columns: repeat(2, 1fr)
- Check gap: 16px

### SQL still SELECT 1
- Check backend logs for schema context
- Verify LLM response in logs
- Check if fallback logic is triggering

### Hover effects not working
- Check CSS transitions
- Verify cursor: pointer on .chart-cell
- Check transform: translateY(-2px)

## Files to Monitor

### Frontend
- `frontend/src/components/Chat.tsx` - JSX for grid
- `frontend/src/components/Chat.css` - CSS styling

### Backend
- `backend/voxquery/core/sql_generator.py` - SQL generation
- `backend/voxquery/core/schema_analyzer.py` - Schema context

## Success Criteria

✅ 2×2 chart grid displays correctly
✅ All 4 chart types show in grid
✅ Click-to-enlarge works
✅ SQL generation produces real queries (not SELECT 1)
✅ Light/dark theme switching works
✅ No console errors
✅ No backend errors
