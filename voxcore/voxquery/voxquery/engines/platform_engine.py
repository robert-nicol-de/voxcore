"""
Platform Engine - Bridges to platform_dialect_engine for SQL dialect handling.
This module provides a unified interface for platform-specific SQL generation and validation.
"""

from ..core.platform_dialect_engine import (
    get_platform_registry,
    get_live_platforms as _get_live_platforms,
    get_coming_soon_platforms as _get_coming_soon_platforms,
    build_system_prompt as _build_system_prompt,
    process_sql as _process_sql,
)


class VoxQueryDialectEngine:
    """Wrapper around platform dialect engine for singleton pattern."""
    
    def __init__(self, config_dir=None):
        """Initialize the dialect engine.
        
        Args:
            config_dir: Path to config directory (for compatibility)
        """
        self.config_dir = config_dir
        self._registry = get_platform_registry()
    
    def build_system_prompt(self, platform, schema_context, whitelist_tables=None, whitelist_columns=None):
        """Build platform-specific system prompt for LLM."""
        return _build_system_prompt(platform, schema_context)
    
    def process_sql(self, llm_output, platform):
        """Validate and rewrite SQL for the platform."""
        result = _process_sql(llm_output, platform)
        return result


def initialize_engine(config_dir=None):
    """Initialize and return the dialect engine.
    
    Args:
        config_dir: Path to config directory
        
    Returns:
        VoxQueryDialectEngine instance
    """
    return VoxQueryDialectEngine(config_dir=config_dir)


def get_live_platforms():
    """Get list of active platforms (ready to use)."""
    return _get_live_platforms()


def get_coming_soon_platforms():
    """Get list of platforms coming soon."""
    return _get_coming_soon_platforms()


# Export platform registry
PLATFORM_REGISTRY = get_platform_registry()


__all__ = [
    'VoxQueryDialectEngine',
    'initialize_engine',
    'get_live_platforms',
    'get_coming_soon_platforms',
    'PLATFORM_REGISTRY',
]
