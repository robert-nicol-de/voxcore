# VoxCore Theme Customization Framework - Phase 2

**Date**: March 1, 2026  
**Status**: Specification Ready (Implementation Q2 2026)  
**Scope**: Admin-level brand customization with governance guardrails

---

## 🎯 Phase 2 Overview

### What Phase 2 Adds
- Admin settings panel for theme customization
- Accent color override (with validation)
- Logo upload and placement
- Sidebar intensity control
- Risk color customization
- Preview system
- Validation framework

### What Phase 2 Preserves
- Core dark/light philosophy
- Professional appearance
- Accessibility standards
- Governance-first messaging
- Security perception

---

## 🛠 Admin Settings Panel Structure

### Location
`/admin/settings/theme` (new route)

### Sections

#### 1. Brand Customization
```
┌─────────────────────────────────────┐
│ Brand Customization                 │
├─────────────────────────────────────┤
│                                     │
│ Logo Upload                         │
│ ┌─────────────────────────────────┐ │
│ │ [Upload PNG/SVG]                │ │
│ │ Current: VoxCore Logo           │ │
│ │ Size: 40px - 200px (auto-scale) │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Accent Color                        │
│ ┌─────────────────────────────────┐ │
│ │ Current: #2563EB (Blue)         │ │
│ │ Presets: [Blue] [Green] [Purple]│ │
│ │ Custom: [Color Picker]          │ │
│ │ Contrast: 5.8:1 ✓ (WCAG AA)    │ │
│ └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

#### 2. Dark Mode Customization
```
┌─────────────────────────────────────┐
│ Dark Mode Settings                  │
├─────────────────────────────────────┤
│                                     │
│ Sidebar Intensity                   │
│ ┌─────────────────────────────────┐ │
│ │ ○ Standard (#0F172A)            │ │
│ │ ○ Darker (#0A0E1A)              │ │
│ │ ○ Deep (#050810)                │ │
│ │ Preview: [Show]                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Risk Colors (Dark Mode)             │
│ ┌─────────────────────────────────┐ │
│ │ Safe: #16A34A [Color Picker]    │ │
│ │ Warning: #F59E0B [Color Picker] │ │
│ │ Danger: #DC2626 [Color Picker]  │ │
│ │ Intensity: [Conservative] [Bold]│ │
│ └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

#### 3. Light Mode Customization
```
┌─────────────────────────────────────┐
│ Light Mode Settings                 │
├─────────────────────────────────────┤
│                                     │
│ Risk Colors (Light Mode)            │
│ ┌─────────────────────────────────┐ │
│ │ Safe: #15803D [Color Picker]    │ │
│ │ Warning: #D97706 [Color Picker] │ │
│ │ Danger: #B91C1C [Color Picker]  │ │
│ │ Intensity: [Conservative] [Bold]│ │
│ └─────────────────────────────────┘ │
│                                     │
│ Note: Backgrounds locked for        │
│ professional appearance             │
│                                     │
└─────────────────────────────────────┘
```

#### 4. Preview & Save
```
┌─────────────────────────────────────┐
│ Preview & Save                      │
├─────────────────────────────────────┤
│                                     │
│ [Preview Dark Mode] [Preview Light] │
│                                     │
│ Validation Status:                  │
│ ✓ Accent contrast: 5.8:1 (WCAG AA) │
│ ✓ Risk colors: Semantic valid      │
│ ✓ Logo: 120px (valid)              │
│                                     │
│ [Cancel] [Save Changes]             │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔐 Validation Framework

### Accent Color Validation
```javascript
validateAccentColor(color) {
  // 1. Check contrast ratio
  const contrast = getContrastRatio(color, bgColor);
  if (contrast < 5.8) {
    return { valid: false, error: "Contrast too low (WCAG AA required)" };
  }
  
  // 2. Check if neon
  const isNeon = checkIfNeon(color);
  if (isNeon) {
    return { valid: false, error: "Neon colors not allowed" };
  }
  
  // 3. Check if professional
  const isProfessional = checkIfProfessional(color);
  if (!isProfessional) {
    return { valid: false, error: "Color not professional enough" };
  }
  
  return { valid: true };
}
```

### Risk Color Validation
```javascript
validateRiskColor(type, color) {
  // 1. Check semantic meaning
  const semanticMatch = checkSemanticMatch(type, color);
  if (!semanticMatch) {
    return { valid: false, error: "Color doesn't match semantic meaning" };
  }
  
  // 2. Check contrast
  const contrast = getContrastRatio(color, bgColor);
  if (contrast < 4.5) {
    return { valid: false, error: "Contrast too low (WCAG AA required)" };
  }
  
  // 3. Check distinctness from other risk colors
  const distinct = checkDistinctness(type, color, otherRiskColors);
  if (!distinct) {
    return { valid: false, error: "Risk colors must be visually distinct" };
  }
  
  return { valid: true };
}
```

### Logo Validation
```javascript
validateLogo(file) {
  // 1. Check file type
  if (!['image/png', 'image/svg+xml'].includes(file.type)) {
    return { valid: false, error: "Only PNG and SVG allowed" };
  }
  
  // 2. Check file size
  if (file.size > 1024 * 1024) { // 1MB
    return { valid: false, error: "File too large (max 1MB)" };
  }
  
  // 3. Check dimensions
  const dimensions = getImageDimensions(file);
  if (dimensions.width < 40 || dimensions.width > 200) {
    return { valid: false, error: "Logo width must be 40-200px" };
  }
  
  return { valid: true };
}
```

---

## 💾 Data Structure

### Admin Theme Settings
```typescript
interface AdminThemeSettings {
  // Brand
  logo?: {
    url: string;
    width: number; // 40-200px
    height: number; // auto-scaled
  };
  
  // Accent
  accentColor: string; // #RRGGBB
  accentValidation: {
    contrast: number;
    wcagLevel: 'AA' | 'AAA';
    isProfessional: boolean;
  };
  
  // Dark Mode
  darkMode: {
    sidebarIntensity: 'standard' | 'darker' | 'deep';
    riskColors: {
      safe: string;
      warning: string;
      danger: string;
    };
    riskIntensity: 'conservative' | 'standard' | 'bold';
  };
  
  // Light Mode
  lightMode: {
    riskColors: {
      safe: string;
      warning: string;
      danger: string;
    };
    riskIntensity: 'conservative' | 'standard' | 'bold';
  };
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}
```

### Database Schema
```sql
CREATE TABLE admin_theme_settings (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL,
  
  -- Brand
  logo_url VARCHAR(255),
  logo_width INT,
  
  -- Accent
  accent_color VARCHAR(7),
  accent_contrast DECIMAL(3,2),
  
  -- Dark Mode
  sidebar_intensity VARCHAR(20),
  dark_safe_color VARCHAR(7),
  dark_warning_color VARCHAR(7),
  dark_danger_color VARCHAR(7),
  dark_risk_intensity VARCHAR(20),
  
  -- Light Mode
  light_safe_color VARCHAR(7),
  light_warning_color VARCHAR(7),
  light_danger_color VARCHAR(7),
  light_risk_intensity VARCHAR(20),
  
  -- Metadata
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  created_by UUID,
  updated_by UUID,
  
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  FOREIGN KEY (updated_by) REFERENCES users(id)
);
```

---

## 🔌 API Endpoints

### Get Current Settings
```
GET /api/v1/admin/theme/settings
Response:
{
  "logo": { "url": "...", "width": 120 },
  "accentColor": "#2563EB",
  "darkMode": { ... },
  "lightMode": { ... }
}
```

### Update Settings
```
PUT /api/v1/admin/theme/settings
Body:
{
  "accentColor": "#3B82F6",
  "darkMode": { ... },
  "lightMode": { ... }
}
Response:
{
  "success": true,
  "validation": { ... },
  "settings": { ... }
}
```

### Upload Logo
```
POST /api/v1/admin/theme/logo
Body: FormData with file
Response:
{
  "success": true,
  "url": "/uploads/logos/org123.png",
  "width": 120,
  "height": 40
}
```

### Preview Settings
```
POST /api/v1/admin/theme/preview
Body:
{
  "accentColor": "#3B82F6",
  "darkMode": { ... }
}
Response:
{
  "cssVariables": { ... },
  "previewUrl": "/preview/theme123"
}
```

### Validate Color
```
POST /api/v1/admin/theme/validate-color
Body:
{
  "type": "accent" | "risk-safe" | "risk-warning" | "risk-danger",
  "color": "#3B82F6",
  "mode": "dark" | "light"
}
Response:
{
  "valid": true,
  "contrast": 5.8,
  "wcagLevel": "AA",
  "warnings": []
}
```

---

## 🎨 CSS Variable Generation

### Current (Phase 1)
```css
:root[data-theme="dark"] {
  --bg-primary: #0F172A;
  --accent-primary: #2563EB;
  --risk-safe: #16A34A;
}
```

### Phase 2 (With Customization)
```css
:root[data-theme="dark"] {
  /* Locked */
  --bg-primary: #0F172A;
  --bg-surface: #111827;
  --text-primary: #F9FAFB;
  
  /* Customizable */
  --accent-primary: var(--custom-accent, #2563EB);
  --risk-safe: var(--custom-risk-safe, #16A34A);
  --risk-warning: var(--custom-risk-warning, #F59E0B);
  --risk-danger: var(--custom-risk-danger, #DC2626);
  
  /* Logo */
  --logo-url: var(--custom-logo-url, none);
  
  /* Sidebar */
  --sidebar-intensity: var(--custom-sidebar-intensity, 1);
}
```

### CSS Variable Injection
```javascript
function applyCustomTheme(settings) {
  const root = document.documentElement;
  
  // Accent
  root.style.setProperty('--custom-accent', settings.accentColor);
  
  // Risk colors
  root.style.setProperty('--custom-risk-safe', settings.darkMode.riskColors.safe);
  root.style.setProperty('--custom-risk-warning', settings.darkMode.riskColors.warning);
  root.style.setProperty('--custom-risk-danger', settings.darkMode.riskColors.danger);
  
  // Logo
  if (settings.logo) {
    root.style.setProperty('--custom-logo-url', `url('${settings.logo.url}')`);
  }
  
  // Sidebar intensity
  root.style.setProperty('--custom-sidebar-intensity', getSidebarIntensity(settings.darkMode.sidebarIntensity));
}
```

---

## 🎯 Implementation Checklist

### Backend
- [ ] Create admin theme settings table
- [ ] Build validation framework
- [ ] Create API endpoints
- [ ] Add logo upload handler
- [ ] Implement CSS variable generation
- [ ] Add audit logging

### Frontend
- [ ] Design admin settings panel
- [ ] Build color picker component
- [ ] Build logo uploader
- [ ] Build preview system
- [ ] Add validation UI
- [ ] Add save/cancel flow

### Testing
- [ ] Unit tests for validation
- [ ] Integration tests for API
- [ ] E2E tests for admin panel
- [ ] Accessibility tests
- [ ] Cross-browser tests

### Documentation
- [ ] Admin user guide
- [ ] API documentation
- [ ] Customization guidelines
- [ ] Troubleshooting guide

---

## 📋 Customization Guidelines

### For Admins

#### Accent Color
- Choose a color that represents your brand
- Must have 5.8:1 contrast ratio (WCAG AA)
- Avoid neon colors
- Test in both dark and light modes

#### Logo
- Use PNG or SVG format
- Keep it simple and recognizable
- Recommended size: 120px width
- Will auto-scale to 40-200px range

#### Sidebar Intensity
- Standard: Default dark navy
- Darker: More intense, deeper navy
- Deep: Maximum intensity, almost black

#### Risk Colors
- Conservative: Muted, professional tones
- Standard: Current palette (recommended)
- Bold: Saturated, more visible tones

### For Designers

#### Accent Color Selection
1. Choose brand primary color
2. Check contrast ratio (must be ≥5.8:1)
3. Verify it's not neon
4. Test in both modes
5. Get admin approval

#### Risk Color Customization
1. Keep semantic meaning (green=safe, yellow=warning, red=danger)
2. Ensure visual distinctness
3. Maintain accessibility
4. Test with colorblind users
5. Document rationale

---

## 🔒 Restrictions & Guardrails

### What CAN Be Customized
✅ Accent color (with validation)  
✅ Logo (with size constraints)  
✅ Sidebar intensity (within dark palette)  
✅ Risk colors (with semantic validation)  

### What CANNOT Be Customized
❌ Core dark/light philosophy  
❌ Background colors  
❌ Text colors  
❌ Accessibility standards  
❌ Governance messaging  
❌ Layout structure  
❌ Animation behavior  

### Why These Restrictions?
- Maintain professional appearance
- Preserve security perception
- Ensure accessibility compliance
- Protect brand consistency
- Prevent gaming dashboard aesthetics

---

## 📊 Rollout Plan

### Week 1: Design & Specification
- [ ] Finalize admin panel design
- [ ] Create API specifications
- [ ] Define validation rules
- [ ] Plan database schema

### Week 2: Backend Implementation
- [ ] Create database tables
- [ ] Build validation framework
- [ ] Implement API endpoints
- [ ] Add logo upload handler

### Week 3: Frontend Implementation
- [ ] Build admin settings panel
- [ ] Create color picker component
- [ ] Build preview system
- [ ] Add validation UI

### Week 4: Testing & Launch
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] User acceptance testing
- [ ] Launch to production

---

## 🚀 Success Metrics

### Adoption
- % of organizations using customization
- Average customization depth
- Time to customize

### Quality
- Validation pass rate
- Support tickets related to customization
- User satisfaction with customization

### Performance
- Theme load time
- CSS variable injection time
- Preview generation time

---

## 📝 Future Enhancements (Phase 3)

### Per-User Preferences
- Allow users to override org theme
- Save user preferences
- Sync across devices

### Theme Scheduling
- Auto-switch dark/light at specific times
- Seasonal themes
- Event-based themes

### Theme Analytics
- Track theme preferences by role
- Measure theme impact on engagement
- Identify popular customizations

### Theme Marketplace
- Share themes between organizations
- Community-created themes
- Theme ratings and reviews

---

## 🎉 Summary

Phase 2 adds admin-level customization while maintaining:
- Professional appearance
- Governance-first messaging
- Accessibility compliance
- Security perception
- Brand consistency

The framework is:
- Scalable (easy to add more customizations)
- Secure (validation prevents bad choices)
- Accessible (WCAG compliance enforced)
- Professional (restrictions prevent gaming aesthetics)

---

**Status**: Specification complete, ready for Phase 2 implementation (Q2 2026)  
**Next**: Test Phase 1, then plan Phase 2 development

