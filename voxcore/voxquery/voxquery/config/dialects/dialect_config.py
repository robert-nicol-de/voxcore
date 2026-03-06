from ...engines.platform_engine import (
    initialize_engine,
    get_live_platforms,
    get_coming_soon_platforms,
    PLATFORM_REGISTRY,
)

# Global dialect engine instance (singleton)
_dialect_engine = None


def get_dialect_config():
    """Get the global dialect configuration engine.
    
    Returns:
        VoxQueryDialectEngine instance
        
    Usage:
        config = get_dialect_config()
        prompt = config.build_system_prompt("sqlserver", schema_context)
        result = config.process_sql(generated_sql, "sqlserver")
    """
    global _dialect_engine
    if _dialect_engine is None:
        _dialect_engine = initialize_engine(config_dir="./voxquery/config/platforms")
    return _dialect_engine


def build_system_prompt(platform, schema_context, whitelist_tables=None, whitelist_columns=None):
    """Build platform-specific system prompt for LLM.
    
    Args:
        platform: "sqlserver", "snowflake", "postgresql", etc.
        schema_context: Schema information to include in prompt
        whitelist_tables: Optional dynamic whitelist
        whitelist_columns: Optional dynamic whitelist
        
    Returns:
        System prompt string with dialect rules
    """
    config = get_dialect_config()
    return config.build_system_prompt(
        platform=platform,
        schema_context=schema_context,
        whitelist_tables=whitelist_tables,
        whitelist_columns=whitelist_columns
    )


def process_sql(llm_output, platform):
    """Validate and rewrite SQL for the platform.
    
    Args:
        llm_output: SQL string from LLM
        platform: Target platform ("sqlserver", "snowflake", etc.)
        
    Returns:
        SQLValidationResult with:
        - is_valid: Boolean
        - final_sql: Rewritten SQL safe for execution
        - was_rewritten: Boolean
        - error_type: Optional error type
        - reason: Human-readable explanation
    """
    config = get_dialect_config()
    return config.process_sql(llm_output, platform)


def get_live_platforms():
    """Get list of active platforms (ready to use)"""
    from voxquery.engines.platform_engine import get_live_platforms as _get_live_platforms
    return _get_live_platforms()


def get_coming_soon_platforms():
    """Get list of platforms coming soon"""
    from voxquery.engines.platform_engine import get_coming_soon_platforms as _get_coming_soon_platforms
    return _get_coming_soon_platforms()


def get_platform_info(platform):
    """Get information about a specific platform.
    
    Args:
        platform: Platform name
        
    Returns:
        Dict with platform info (status, label, config_file, etc.)
    """
    if platform not in PLATFORM_REGISTRY:
        raise ValueError(f"Unknown platform: {platform}")
    return PLATFORM_REGISTRY[platform]


def get_all_platforms():
    """Get all platforms (both live and coming soon)"""
    return PLATFORM_REGISTRY


__all__ = [
    'get_dialect_config',
    'build_system_prompt',
    'process_sql',
    'get_live_platforms',
    'get_coming_soon_platforms',
    'get_platform_info',
    'get_all_platforms',
]
