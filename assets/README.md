# VoxQuery Assets Hub

Master repository for all VoxQuery visual and data assets. This is the **single source of truth** for branding across the entire system.

## Directory Structure

```
assets/
├── brand/              ← 🎯 Master brand files (primary logos, icons, favicon)
│   ├── logo-primary.svg     (Full logo with text — main hero usage)
│   ├── logo-compact.svg     (Compact horizontal logo — header/nav)
│   ├── logo-icon.svg        (Icon only — favicons, buttons, badges)
│   ├── logo-compact-mono.svg (Monochrome variant — light backgrounds)
│   └── favicon.svg          (Favicon master — convert to .ico for browsers)
│
├── design/             ← 🎨 Design system tokens
│   └── tokens.json          (Colors, spacing, typography, shadows, animations)
│
├── marketing/          ← 📢 Marketing & promotional assets
│   ├── hero-image.png       (Homepage hero image)
│   ├── demo-screenshot.png  (Product screenshot for marketing)
│   └── social-preview.png   (OG image for social sharing)
│
└── demo/               ← 📊 Sample data for playground
    ├── sample-sales-data.json   (Example JSON dataset)
    └── sample-sales-data.csv    (Example CSV for import)
```

## Usage Guide

### 1️⃣ Brand Assets (Frontend)

Use logos from `/brand/` in your React components:

```tsx
import logo from '/assets/brand/logo-primary.svg'
import logoCompact from '/assets/brand/logo-compact.svg'
import icon from '/assets/brand/logo-icon.svg'

export default function Header() {
  return (
    <div>
      <img src={logoCompact} alt="VoxQuery" />
    </div>
  )
}
```

### 2️⃣ Design Tokens (Tailwind/CSS)

Reference tokens in your design decisions:

```json
{
  "primary": "#3B82F6",          // Electric blue
  "accent": "#06B6D4",           // Cyan accent
  "success": "#22C55E",          // Green
  "warning": "#F59E0B",          // Amber
  "danger": "#EF4444"            // Red
}
```

### 3️⃣ Marketing Assets

Place hero images, screenshots, and social meta images here for consistency.

### 4️⃣ Demo Data

Use sample datasets to populate the Playground without requiring live database connections:

```json
{
  "metadata": { "name": "Sales Trends" },
  "rows": [ /* sample data */ ]
}
```

## Asset Sync Strategy

To keep builds fresh:

1. **Frontend**: Symlink or copy from `/assets/brand/` during build
2. **Public Folder**: Point `/public/assets/` to root `/assets/` or copy on deploy
3. **Backend**: Include demo data in `/assets/demo/` for fallback responses

## File Format Requirements

| Asset Type | Format | Purpose |
|------------|--------|---------|
| Logo (Primary) | SVG | Scalable, web-native |
| Logo (Icon) | SVG | Favicons, UI elements |
| Logo (Mono) | SVG | Dark/light backgrounds |
| Design Tokens | JSON | Design system source |
| Images | PNG/WebP | Compressed for web |
| Demo Data | JSON/CSV | Playground datasets |

## Deployment Checklist

- [ ] Design tokens in `/assets/design/tokens.json`
- [ ] Master logos in `/assets/brand/`
- [ ] Favicon created from `/assets/brand/favicon.svg`
- [ ] Frontend build pulls logos from this hub
- [ ] Demo data available for Playground fallback
- [ ] Social preview image ready in `/assets/marketing/`

## Next Steps

1. Replace placeholder SVGs with official brand artwork
2. Add marketing hero image to `/assets/marketing/`
3. Create additional demo datasets for different DB platforms
4. Set up automated favicon generation from master SVG
5. Configure Tailwind to reference `tokens.json` for colors

---

**Last Updated:** March 2026  
**Owner:** Design & Product Team
