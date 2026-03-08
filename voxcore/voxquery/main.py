"""Main entry point for VoxQuery API"""

# Force UTF-8 encoding on Windows
import sys
import io

# Set stdout/stderr to UTF-8 with error replacement
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from voxcore.voxquery.voxquery.api import app
from voxcore.voxquery.voxquery.settings import settings

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "voxcore.voxquery.voxquery.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
