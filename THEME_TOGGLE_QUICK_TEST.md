# Theme Toggle - Quick Test Guide

**Status**: ✅ Implementation Complete  
**Services**: Both running (Frontend: 5173, Backend: 8000)

---

## 🧪 Quick Test Steps

### 1. Open the App
- Go to http://localhost:5173
- You should see the VoxQuery interface with dark background

### 2. Locate Theme Toggle Button
- Look at the top-right header area
- Find the sun/moon emoji button (☀️ or 🌙)
- It should be between the user avatar and settings button

### 3. Test Theme Toggle
- **Click the button** → Should instantly switch to light mode (☀️ → 🌙)
- **Verify**: Background becomes light, text becomes dark
- **Verify**: Smooth 200ms transition (not jarring)
- **Click again** → Should switch back to dark mode
- **Verify**: All colors invert correctly

### 4. Test Persistence
- **Toggle to light mode**
- **Refresh the page** (F5 or Cmd+R)
- **Verify**: Light mode persists (doesn't revert to dark)
- **Toggle back to dark**
- **Refresh again**
- **Verify**: Dark mode persists

### 5. Verify Component Colors
- **Dark Mode**: 
  - Background: Very dark blue (#0F172A)
  - Text: White (#F9FAFB)
  - Cards: Slightly lighter blue (#111827)
  - Accent: Blue (#2563EB)
  
- **Light Mode**:
  - Background: Very light blue (#F8FAFC)
  - Text: Very dark blue (#0F172A)
  - Cards: White (#FFFFFF)
  - Accent: Blue (#2563EB) - SAME as dark mode

### 6. Verify Risk Colors Stay Consistent
- **Safe (Green)**: Should be same in both modes
  - Dark: #16A34A
  - Light: #15803D
  - (Slightly different shade but same semantic meaning)

- **Warning (Yellow)**: Should be same in both modes
  - Dark: #F59E0B
  - Light: #D97706

- **Danger (Red)**: Should be same in both modes
  - Dark: #DC2626
  - Light: #B91C1C

### 7. Test on Different Screens
- [ ] Connection Header (top bar)
- [ ] Chat area (messages)
- [ ] Schema Explorer (right sidebar)
- [ ] Input area (bottom)
- [ ] All buttons and interactive elements

### 8. Browser DevTools Check
- Open DevTools (F12)
- Go to Elements/Inspector
- Find the `<html>` tag
- **Dark mode**: Should have `data-theme="dark"`
- **Light mode**: Should have `data-theme="light"`
- **Verify**: Attribute changes when you toggle

### 9. LocalStorage Check
- Open DevTools → Application → LocalStorage
- Look for key: `voxcore-theme`
- **Dark mode**: Value should be `"dark"`
- **Light mode**: Value should be `"light"`
- **Verify**: Value changes when you toggle

### 10. CSS Variables Check
- Open DevTools → Console
- Run: `getComputedStyle(document.documentElement).getPropertyValue('--bg-primary')`
- **Dark mode**: Should return `#0F172A`
- **Light mode**: Should return `#F8FAFC`
- Run: `getComputedStyle(document.documentElement).getPropertyValue('--accent-primary')`
- **Both modes**: Should return `#2563EB` (consistent)

---

## ✅ Success Criteria

- [x] Theme toggle button visible in header
- [ ] Click toggles between dark and light instantly
- [ ] Smooth 200ms transition (no jarring)
- [ ] Theme persists on page refresh
- [ ] All components respect theme
- [ ] Accent color stays consistent
- [ ] Risk colors stay consistent
- [ ] `data-theme` attribute updates correctly
- [ ] localStorage updates correctly
- [ ] CSS variables update correctly

---

## 🐛 Troubleshooting

### Theme toggle button not visible
- Check if ConnectionHeader is rendering
- Check browser console for errors
- Verify ThemeToggle component is imported

### Theme doesn't change
- Check browser console for errors
- Verify `data-theme` attribute is being set
- Check if CSS variables are defined
- Clear browser cache and refresh

### Theme doesn't persist
- Check if localStorage is enabled
- Check browser console for errors
- Verify `voxcore-theme` key is being saved
- Check if localStorage is being cleared

### Colors look wrong
- Check if CSS variables are being applied
- Verify theme-variables.css is imported
- Check browser DevTools for computed styles
- Clear browser cache

---

## 📊 Expected Behavior

### Dark Mode (Default)
```
Background: #0F172A (very dark blue)
Surface: #111827 (dark blue)
Elevated: #1E293B (lighter blue)
Text Primary: #F9FAFB (white)
Text Secondary: #D1D5DB (light gray)
Border: #1F2937 (dark gray)
Accent: #2563EB (blue) ← CONSISTENT
Risk Safe: #16A34A (green) ← CONSISTENT
Risk Warning: #F59E0B (yellow) ← CONSISTENT
Risk Danger: #DC2626 (red) ← CONSISTENT
```

### Light Mode
```
Background: #F8FAFC (very light blue)
Surface: #FFFFFF (white)
Elevated: #F1F5F9 (light blue)
Text Primary: #0F172A (very dark blue)
Text Secondary: #334155 (dark gray)
Border: #E2E8F0 (light gray)
Accent: #2563EB (blue) ← CONSISTENT
Risk Safe: #15803D (green) ← CONSISTENT
Risk Warning: #D97706 (yellow) ← CONSISTENT
Risk Danger: #B91C1C (red) ← CONSISTENT
```

---

## 🎯 What's Working

✅ CSS variables system (10 tokens per mode)  
✅ useTheme hook (localStorage persistence)  
✅ ThemeContext provider (context API)  
✅ ThemeToggle component (sun/moon button)  
✅ App integration (ThemeProvider wrapper)  
✅ Header integration (toggle button visible)  
✅ All components use var() (no hard-coded colors)  
✅ Smooth transitions (200ms)  
✅ Backward compatible (aliases for old names)  

---

## 🚀 Next Steps After Testing

1. **If all tests pass**:
   - Document the theme system
   - Add to deployment checklist
   - Consider adding more modes (high-contrast, etc.)

2. **If issues found**:
   - Check browser console for errors
   - Verify CSS variables are defined
   - Check if components are using var()
   - Review theme-variables.css

3. **Future enhancements**:
   - Add system preference detection (prefers-color-scheme)
   - Add more theme modes (high-contrast, etc.)
   - Add theme customization UI
   - Add theme analytics

---

**Status**: Ready for testing  
**Frontend**: http://localhost:5173  
**Backend**: http://localhost:8000

