# Quick Action Guide - Deploy & Test

## What Was Fixed

### Fix 1: Chart Buttons in Input Row
- Input box takes most width
- 4 chart buttons (Bar, Pie, Line, Comparison) on right
- Buttons disabled (greyed) until results exist
- Buttons active (blue) after query
- Click to enlarge in modal

### Fix 2: Force Real SQL Generation
- Stronger, simpler prompt
- Aggressive safety net catches invalid output
- Hallucinated tables detected and replaced
- Direct schema fetch fallback
- No more SELECT 1

---

## Deploy (2 minutes)

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Then:
python backend/main.py
```

### Step 2: Frontend Auto-Reload
- If dev server running: changes auto-reload
- If not: `npm run dev` in frontend directory

---

## Test (5 minutes)

### Test 1: Chart Buttons
1. Open frontend
2. Connect to database
3. Look at input area
4. Should see: [Input Box] [Bar] [Pie] [Line] [Comparison] [Send]
5. Buttons should be greyed out (disabled)

### Test 2: Query Generation
1. Ask: "Show me the top 10 records"
2. Check backend logs for: `Extracted SQL: SELECT * FROM ...`
3. Should NOT see: `SELECT 1`
4. Results should display

### Test 3: Chart Buttons Activate
1. After query completes
2. Chart buttons should turn BLUE (active)
3. Click any button
4. Modal should open with chart type
5. Click × or outside to close

### Test 4: Different Questions
1. Ask: "How many rows are in the database?"
2. Ask: "Show me the latest records"
3. Each should generate real SQL
4. Chart buttons should work

---

## Expected Results

### Before
```
❌ Buttons: Not visible
❌ LLM: SELECT 1
❌ Charts: [object Object]
```

### After
```
✅ Buttons: Visible, greyed, then blue
✅ LLM: SELECT * FROM FACT_REVENUE LIMIT 10
✅ Charts: Click to enlarge in modal
```

---

## Troubleshooting

### If buttons don't appear
1. Check browser console for errors
2. Verify CSS loaded (F12 → Elements)
3. Hard refresh: Ctrl+Shift+R

### If LLM still outputs SELECT 1
1. Check backend logs for schema context
2. Verify database connection
3. Look for error messages in logs
4. Check if schema_analyzer has tables

### If modal doesn't open
1. Check browser console for errors
2. Verify onClick handlers firing
3. Try hard refresh
4. Check z-index conflicts

---

## Log Locations

### Backend Logs
- Console output when running `python backend/main.py`
- Look for:
  - `✅ Schema loaded: X chars`
  - `Extracted SQL: SELECT ...`
  - `✅ Forced safe fallback` (if triggered)

### Frontend Logs
- Browser DevTools Console (F12)
- Look for any red errors
- Check Network tab for API responses

---

## Files Modified

1. `frontend/src/components/Chat.tsx` - Input row + buttons
2. `frontend/src/components/Chat.css` - Styling
3. `backend/voxquery/core/sql_generator.py` - Prompt + safety net

---

## Success Checklist

- [ ] Backend starts without errors
- [ ] Chart buttons visible in input row
- [ ] Buttons greyed out initially
- [ ] Query generates real SQL (not SELECT 1)
- [ ] Buttons turn blue after query
- [ ] Click button opens modal
- [ ] Modal closes with × button
- [ ] No console errors
- [ ] KPI cards display

---

## Next Steps

1. ✅ Restart backend
2. ✅ Test chart buttons
3. ✅ Test SQL generation
4. ✅ Monitor logs
5. ✅ Test different questions

**Ready to deploy!**
