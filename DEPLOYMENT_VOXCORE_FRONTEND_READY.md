# VoxCore Frontend Deployment Guide

## Current Status
**Built Frontend**: ✓ Ready at `frontend/dist/`
**cPanel Deployment**: ✗ Skeleton index.html only

## Files Ready to Deploy
```
frontend/dist/
├── index.html (Vite-compiled)
├── assets/
│   ├── index-a0fe369a.js (React app bundle)
│   └── index-978f01c1.css (Styles)
└── *.svg and *.png (assets)
```

## Deployment Steps

### Option A: Manual Upload to cPanel
1. Connected to cPanel via FTP/SFTP
2. Navigate to `~/public_html/voxcore/`
3. Delete old/skeleton `index.html`
4. Upload entire `frontend/dist/` contents:
   - Copy `index.html`
   - Copy `assets/` folder
   - Copy image assets (*.svg, *.png)

### Option B: Automated Sync (if using git)
```bash
rsync -avz frontend/dist/ user@voxcore.org:~/public_html/voxcore/
```

## .htaccess Configuration (Already in place)
```apache
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [QSA,L]
</IfModule>
```
✓ Routes API requests to backend
✓ Serves index.html for SPA routes

## Backend Health Check
```bash
curl https://voxcore.org/api/health
```

## What Will Display After Deployment
- VoxQuery login page ✓
- Ask Query interface ✓
- Results dashboard ✓
- Settings modal with Apply button ✓ (just added)
- Governance logs ✓

## Next Steps
1. Upload dist folder to cPanel
2. Verify https://voxcore.org/ loads the app
3. Test API connectivity
4. Confirm settings/apply button shows
