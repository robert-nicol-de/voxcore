# 🚀 VoxQuery - Three Ways to Run It

## Option 1: Simple Launcher (Easiest) ⭐

**No setup needed - just double-click!**

```
VoxQuery/
└── START_VOXQUERY.bat  ← Double-click this
```

This automatically:
- Starts the backend
- Starts the frontend  
- Opens your browser
- Shows you everything running

✅ **No terminal windows**  
✅ **One-click startup**  
✅ **Automatic browser opening**

---

## Option 2: Python Launcher

If the .bat file doesn't work, use Python directly:

```bash
cd c:\Users\USER\Documents\trae_projects\VoxQuery
python launcher.py
```

Same result as Option 1, but run from terminal.

---

## Option 3: Standalone .exe (Most Professional)

Build a single executable that runs just the backend:

### Step 1: Build it (one-time only)
```bash
cd c:\Users\USER\Documents\trae_projects\VoxQuery\backend
python build_exe.py
```

This creates: `backend\dist\VoxQuery.exe`

### Step 2: Run it
Just double-click `VoxQuery.exe` to start the backend API.

### Step 3: Start frontend separately
```bash
cd frontend
npm run dev
```

### Step 4: Open browser
Go to http://localhost:5173

---

## Quick Comparison

| Method | Ease | Setup | Features |
|--------|------|-------|----------|
| **START_VOXQUERY.bat** | ⭐⭐⭐ | 0 min | Auto-starts both, opens browser |
| **launcher.py** | ⭐⭐ | 1 min | Auto-starts both, shows terminal |
| **VoxQuery.exe** | ⭐⭐ | 5 min build | Backend only, professional |
| **Manual terminal** | ⭐ | 2 min | Full control |

---

## Getting Started

### Right Now (Easiest)
1. Open Windows Explorer
2. Navigate to: `c:\Users\USER\Documents\trae_projects\VoxQuery`
3. **Double-click: `START_VOXQUERY.bat`**
4. Wait 10 seconds
5. Browser opens automatically
6. Start typing questions!

### If .bat doesn't work
```bash
python launcher.py
```

### If you want a real .exe (5 min build)
```bash
cd backend
python build_exe.py
# Wait for build to complete
# Then double-click dist\VoxQuery.exe
```

---

## Troubleshooting

**"Command not found" with .bat?**
- Make sure Python is installed
- Check: `python --version` in terminal

**.exe build fails?**
- Install PyInstaller: `pip install pyinstaller`
- Then try again: `python build_exe.py`

**Frontend won't start?**
- Install Node.js from nodejs.org
- Run `npm install` in frontend/ directory

**Port already in use?**
- Edit backend/.env
- Change API_PORT to 8001
- Change VITE_API_URL to http://localhost:8001

---

## What's Running

When you start:

| Service | URL | What it does |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | Talks to databases, generates SQL |
| **Frontend** | http://localhost:5173 | The chat interface you see |
| **API Docs** | http://localhost:8000/docs | Interactive API docs |

---

## Stop It

**If using .bat:** Close the console windows  
**If using launcher.py:** Press Ctrl+C  
**If using .exe:** Close the console window  

---

## Pro Tip

**Create a shortcut:**
1. Right-click `START_VOXQUERY.bat`
2. Click "Create shortcut"
3. Move to Desktop
4. Double-click anytime to start VoxQuery!

---

**Ready? → Double-click START_VOXQUERY.bat!**
