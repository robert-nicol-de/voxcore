# ECharts Chart Display Fix Guide

## Current Setup
- **Chart Library:** ECharts (installed)
- **Component:** ChartRenderer.tsx
- **Usage:** Chat.tsx renders 4 chart types (Bar, Pie, Line, Comparison)

## Expected Data Structure

ChartRenderer expects this structure for **bar charts**:
```javascript
{
  type: 'bar',
  title: 'Query Results',
  xAxis: {
    data: ['Product A', 'Product B', 'Product C']  // Array of labels
  },
  yAxis: {
    name: 'Value',
    type: 'value'
  },
  series: [
    {
      data: [100, 200, 150],  // Array of numbers
      type: 'bar',
      name: 'Value'
    }
  ]
}
```

## What Backend Returns

Check `voxcore/voxquery/voxquery/api/v1/query.py` lines 100-150 to verify the chart structure matches.

## Quick Diagnostic

**Step 1: Open Browser DevTools**
- Press F12
- Go to Console tab
- Look for RED errors

**Step 2: Test Backend Response**
In browser console, run:
```javascript
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
.then(data => {
  console.log('Full response:', data);
  console.log('Chart structure:', data.chart);
  console.log('xAxis:', data.chart?.xAxis);
  console.log('series:', data.chart?.series);
})
```

**Step 3: Verify Structure**
Check if the response has:
- ✅ `chart.type` = 'bar'
- ✅ `chart.xAxis.data` = array of strings
- ✅ `chart.series[0].data` = array of numbers
- ✅ `chart.yAxis.name` = string

## Most Likely Issues

### Issue 1: xAxis.data is not an array
**Symptom:** Chart renders but shows no bars
**Fix:** Ensure backend returns `xAxis: { data: [...] }`

### Issue 2: series[0].data is not an array of numbers
**Symptom:** Chart renders but shows no bars
**Fix:** Ensure all values are numbers, not strings

### Issue 3: ECharts not initializing
**Symptom:** Chart container is blank
**Fix:** Check browser console for errors

### Issue 4: Chart container has no size
**Symptom:** Chart renders but invisible
**Fix:** ChartRenderer sets height: 400px, should be visible

## Testing Steps

1. **Open http://localhost:5173**
2. **Connect to SQL Server**
3. **Ask a question:** "Show top 5 products by sales"
4. **Open DevTools (F12)**
5. **Check Console for errors**
6. **Run diagnostic script above**
7. **Share the output**

## If Charts Still Don't Display

Share:
1. Browser console error (if any)
2. Backend response structure (from diagnostic script)
3. Screenshot of what you see

With this info, I can give you the exact fix.

## Quick Fix Checklist

- [ ] Backend running on port 5000
- [ ] Frontend running on port 5173
- [ ] Connected to SQL Server
- [ ] Asked a question
- [ ] Opened DevTools (F12)
- [ ] Checked Console for errors
- [ ] Ran diagnostic script
- [ ] Verified chart data structure

**Next:** Run the diagnostic and share what you find.
