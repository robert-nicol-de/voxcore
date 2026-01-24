"""
Build VoxQuery as a standalone .exe file using PyInstaller
Run this once: python build_exe.py
Then use: dist/VoxQuery.exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Build the VoxQuery backend as a standalone executable"""
    
    print("🔨 Building VoxQuery.exe...")
    print("=" * 60)
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    dist_dir = backend_dir / "dist"
    build_dir = backend_dir / "build"
    
    # Remove old builds
    if dist_dir.exists():
        print("Removing old dist directory...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build with PyInstaller
    print("\nRunning PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        "VoxQuery",
        "--icon=NONE",
        "--add-data",
        f"{backend_dir / '.env.example'}{os.pathsep}.",
        "--add-data",
        f"{backend_dir / 'requirements.txt'}{os.pathsep}.",
        "--collect-all",
        "voxquery",
        "--collect-all",
        "sqlalchemy",
        "--collect-all",
        "langchain",
        "--hidden-import=sqlalchemy",
        "--hidden-import=langchain",
        "--hidden-import=snowflake.connector",
        "--hidden-import=psycopg2",
        "--hidden-import=google.cloud.bigquery",
        "--hidden-import=pyodbc",
        str(backend_dir / "main.py")
    ]
    
    result = subprocess.run(cmd, cwd=backend_dir)
    
    if result.returncode == 0:
        exe_path = dist_dir / "VoxQuery.exe"
        if exe_path.exists():
            print("\n" + "=" * 60)
            print("✅ SUCCESS! VoxQuery.exe created")
            print("=" * 60)
            print(f"\n📍 Location: {exe_path}")
            print(f"\n🎯 Next steps:")
            print(f"   1. Copy to desktop or anywhere convenient")
            print(f"   2. Double-click VoxQuery.exe to start")
            print(f"   3. Backend starts automatically")
            print(f"   4. Browser opens to http://localhost:5173")
            print(f"\n💡 Note: This only includes the backend.")
            print(f"   Frontend (React) still needs: npm run dev in frontend/")
            return True
    
    print("\n❌ Build failed. Check errors above.")
    return False

if __name__ == "__main__":
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    build_exe()
