# Duplicate Charts Fix - 2x2 Grid Issue

## Problem

The 2x2 chart grid was showing the same chart results in multiple positions, creating a confusing user experience. This happened when:
- Data had insufficient variety (only 1 unique value in the category column)
- Multiple chart types were being generated from the same limited data
- All charts ended up showing identical results

## Root Cause

The `generate_all_charts()` function in `backend/voxquery/formatting/charts.py` was generating 4 chart types (bar, pie, line, comparison) regardless of data variety. When data had only 1 unique category value, all 4 charts would show the same single bar/slice, creating visual duplication.

## Solution

Added a data variety check before generating multiple charts:

```python
# Check if data is too small for multiple charts (avoid duplicates)
unique_x_values = len(set(str(row.get(x_col, "")) for row in data))
has_sufficient_data = unique_x_values > 1 and len(data) > 1

# Only generate multiple charts if we have sufficient data variety
if not has_sufficient_data:
    logger.info(f"Insufficient data variety for multiple charts (unique values: {unique_x_values}). Returning single bar chart.")
    # Return only the bar chart
    return specs
```

## Changes Made

**File:** `backend/voxquery/formatting/charts.py`

**Function:** `generate_all_charts()`

**Changes:**
1. Added `unique_x_values` calculation to count distinct category values
2. Added `has_sufficient_data` check (requires > 1 unique value AND > 1 row)
3. If insufficient data, return only the bar chart (avoids duplicates)
4. If sufficient data, generate all 4 chart types as before

## Behavior

### Before Fix
- Query with 1 account: Shows 4 identical charts (bar, pie, line, comparison)
- Query with 5 accounts: Shows 4 different charts ✓

### After Fix
- Query with 1 account: Shows 1 bar chart (clean, no duplicates) ✓
- Query with 5 accounts: Shows 4 different charts ✓

## Benefits

✅ **Eliminates visual duplication** - No more 2x2 grid with identical charts
✅ **Cleaner UI** - Single chart when data is limited
✅ **Better UX** - Users see relevant visualizations for their data
✅ **Backward compatible** - Doesn't break existing functionality
✅ **Logging** - Logs when insufficient data is detected

## Testing

The fix automatically handles:
- Single row queries → 1 bar chart
- Single category queries → 1 bar chart
- Multiple categories → 4 different charts (bar, pie, line, comparison)

## Deployment

1. Restart backend: `python backend/main.py`
2. Test with a query that returns 1 account/category
3. Verify only 1 chart is shown (not 4 duplicates)
4. Test with a query that returns multiple categories
5. Verify 4 different charts are shown

## Status

✅ Code implemented
✅ Compiles successfully
✅ Ready for deployment

---

**File Modified:** `backend/voxquery/formatting/charts.py`
**Lines Changed:** ~50
**Complexity:** Low
**Risk:** Low
**Impact:** High (improves UX significantly)
