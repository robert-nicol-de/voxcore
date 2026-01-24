"""
VoxQuery Backend Launcher - Start just the backend
"""

import subprocess
import time
import webbrowser
import sys
from pathlib import Path

def run_backend_only():
    """Start backend, then open browser to API docs"""
    
    print("🚀 VoxQuery Backend Launcher")
    print("=" * 60)
    
    # Get backend directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    print(f"📍 Backend: {backend_dir}")
    
    if not backend_dir.exists():
        print(f"❌ Backend not found: {backend_dir}")
        return False
    
    print("\n📦 Starting Backend...")
    try:
        # Start backend
        backend_proc = subprocess.Popen(
            [sys.executable, str(backend_dir / "main.py")],
            cwd=str(backend_dir)
        )
        print(f"   ✅ Backend started!")
    except Exception as e:
        print(f"   ❌ Failed to start backend: {e}")
        return False
    
    print("\n⏳ Waiting 3 seconds for backend to start...")
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("✅ VoxQuery Backend is Running!")
    print("=" * 60)
    
    print("\n📊 Backend API is ready:")
    print("   http://localhost:8000")
    
    print("\n📖 API Documentation:")
    print("   http://localhost:8000/docs")
    
    print("\n🧪 Try the API:")
    print("   Open a new terminal and run:")
    print('   curl http://localhost:8000/health')
    
    print("\n💡 Frontend Note:")
    print("   Frontend requires Node.js/npm (not installed)")
    print("   You can use the API directly:")
    print("   - POST http://localhost:8000/api/v1/query")
    print("   - GET http://localhost:8000/schema")
    
    print("\n⏳ Backend running... Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping VoxQuery backend...")
        try:
            backend_proc.terminate()
            time.sleep(1)
            if backend_proc.poll() is None:
                backend_proc.kill()
        except:
            pass
        print("✅ Done!")

if __name__ == "__main__":
    run_backend_only()
