# VoxCore config.py

import os

class Settings:
    PROJECT_NAME: str = "VoxCore API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("VOXCORE_DEBUG", "false").lower() == "true"
    # Add more settings as needed

settings = Settings()
