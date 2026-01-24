"""
VoxQuery Launcher - One-click to start everything
Double-click this file or run: python launcher.py
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def run_launcher():
    """Start backend and frontend in background, then open browser"""
    
    print("🚀 VoxQuery Launcher")
    print("=" * 60)
    
    # Get project root (same directory as launcher.py)
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"
    
    print(f"📍 Project: {project_root}")
    
    # Check if directories exist
    if not backend_dir.exists():
        print(f"❌ Backend not found: {backend_dir}")
        return False
    
    if not frontend_dir.exists():
        print(f"❌ Frontend not found: {frontend_dir}")
        return False
    
    print("\n📦 Starting Backend...")
    try:
        # Start backend in background
        backend_proc = subprocess.Popen(
            [sys.executable, str(backend_dir / "main.py")],
            cwd=str(backend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print(f"   ✅ Backend started (PID: {backend_proc.pid})")
    except Exception as e:
        print(f"   ❌ Failed to start backend: {e}")
        return False
    
    print("\n⏳ Waiting for backend to start (3 seconds)...")
    time.sleep(3)
    
    print("\n📦 Starting Frontend...")
    try:
        # Start frontend in background
        frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print(f"   ✅ Frontend started (PID: {frontend_proc.pid})")
    except Exception as e:
        print(f"   ❌ Failed to start frontend: {e}")
        print(f"   ℹ️  Make sure Node.js and npm are installed")
        return False
    
    print("\n⏳ Waiting for frontend to start (5 seconds)...")
    time.sleep(5)
    
    print("\n" + "=" * 60)
    print("✅ VoxQuery is Running!")
    print("=" * 60)
    print("\n🌐 Opening http://localhost:5173 in your browser...")
    
    try:
        webbrowser.open("http://localhost:5173")
    except Exception as e:
        print(f"   ⚠️  Could not open browser automatically: {e}")
        print(f"   📍 Open manually: http://localhost:5173")
    
    print("\n📊 What's Running:")
    print("   Backend API:  http://localhost:8000")
    print("   Frontend UI:  http://localhost:5173")
    print("   API Docs:     http://localhost:8000/docs")
    
    print("\n💡 To stop everything:")
    print("   Press Ctrl+C in both console windows")
    
    print("\n⏳ Press Ctrl+C to exit this launcher...")
    try:
        # Keep running until user stops
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping VoxQuery...")
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
            time.sleep(1)
            backend_proc.kill()
            frontend_proc.kill()
        except:
            pass
        print("✅ Done!")

if __name__ == "__main__":
    run_launcher()
