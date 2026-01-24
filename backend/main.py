"""Main entry point for VoxQuery API"""

from voxquery.api import app
from voxquery.config import settings

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "voxquery.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
