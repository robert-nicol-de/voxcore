# Chart Display Diagnostic - ECharts Issue

## Status
✅ **ECharts is installed** (verified via npm install)
✅ **ChartRenderer component exists** and uses echarts correctly
✅ **Backend is running** (port 5000)
✅ **Frontend is running** (port 5173)

## What We Found

**Chart Library:** ECharts (not Recharts)
- File: `frontend/src/components/ChartRenderer.tsx`
- Library: `import * as echarts from 'echarts'`
- Container height: 400px
- Supported types: bar, pie, line, scatter

## Why Charts Might Not Be Displaying

### Most Likely Causes (in order):

1. **Chart data not being passed correctly**
   - Backend returns chart object but structure doesn't match expectations
   - Check: Does `chart.xAxis.data` exist?
   - Check: Does `chart.series[0].data` exist?

2. **ECharts container not rendering**
   - Container div exists but echarts.init() fails silently
   - Check browser console for errors (F12 > Console)

3. **CSS/Styling issue**
   - Chart renders but is hidden by CSS
   - Check: Is container visible? (width: 100%, height: 400px)

4. **Data structure mismatch**
   - Backend sends data in wrong format
   - Expected: `{ type: 'bar', xAxis: { data: [...] }, series: [{ data: [...] }] }`

## Quick Diagnostic Steps

### Step 1: Check Browser Console
1. Open http://localhost:5173
2. Press F12 to open DevTools
3. Click "Console" tab
4. Look for RED error messages
5. Copy any errors and share them

### Step 2: Test Chart Data
In browser console, run:
```javascript
// Check if chart data exists
console.log('Chart data:', window.__chartData);

// Or check the response from backend
fetch('http://localhost:5000/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Show top 5 products by sales',
    warehouse: 'sqlserver',
    session_id: 'test'
  })
})
.then(r => r.json())
.then(data => console.log('Backend response:', data))
```

### Step 3: Verify Chart Structure
Expected response from backend:
```json
{
  "success": true,
  "chart": {
    "type": "bar",
    "title": "Query Results",
    "xAxis": { "data": ["Product A", "Product B", ...] },
    "yAxis": { "name": "Value", "type": "value" },
    "series": [{ "data": [100, 200, ...], "type": "bar", "name": "Value" }]
  }
}
```

## Files to Check

1. **Backend chart generation:** `voxcore/voxquery/voxquery/api/v1/query.py`
   - Lines 100-150: Chart building logic
   - Verify: `chart_labels` and `chart_values` are populated

2. **Frontend chart rendering:** `frontend/src/components/ChartRenderer.tsx`
   - Lines 9-50: useEffect hook
   - Verify: `buildChartOption()` returns valid echarts config

3. **Chat component:** `frontend/src/components/Chat.tsx`
   - Verify: Chart is being passed to ChartRenderer
   - Check: `<ChartRenderer chart={chart} />`

## Next Actions

**Option A: Check Console Errors (5 minutes)**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for RED errors
4. Share the exact error message

**Option B: Test Backend Response (5 minutes)**
1. Run the test query in browser console (see Step 2 above)
2. Check if `chart` object exists in response
3. Verify structure matches expected format

**Option C: Verify Chart is Being Passed (5 minutes)**
1. Add console.log in Chat.tsx: `console.log('Chart:', chart)`
2. Check if chart object appears in console
3. Verify it has `xAxis`, `series`, etc.

## Common Fixes

**If echarts not found:**
```bash
npm install echarts
npm run dev
```

**If chart renders but shows no data:**
- Check data structure in backend response
- Verify `xAxis.data` is an array
- Verify `series[0].data` is an array of numbers

**If chart container is blank:**
- Check browser console for errors
- Verify container has width/height
- Try refreshing page (Ctrl+Shift+R)

## Status Summary

- ✅ ECharts installed
- ✅ ChartRenderer component ready
- ✅ Backend running
- ✅ Frontend running
- ❓ Chart data structure (needs verification)
- ❓ Browser console errors (needs checking)

**Next step:** Check browser console for errors and share what you see.
