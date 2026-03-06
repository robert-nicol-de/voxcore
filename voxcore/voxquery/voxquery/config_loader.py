"""Configuration loader for database connections from INI files"""

import configparser
import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Load database configurations from INI files"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Try to find config directory relative to this file
            current_dir = Path(__file__).parent.parent  # voxquery -> backend
            config_dir = str(current_dir / "config")
        
        self.config_dir = Path(config_dir)
        self.configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all INI files from config directory and dialects subdirectory"""
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            return
        
        # Load from main config directory
        for ini_file in self.config_dir.glob("*.ini"):
            db_type = ini_file.stem  # filename without extension
            try:
                self.configs[db_type] = self._parse_ini(ini_file)
                logger.info(f"✓ Loaded config: {db_type}")
            except Exception as e:
                logger.error(f"✗ Failed to load config {db_type}: {e}")
        
        # Load from dialects subdirectory
        dialects_dir = self.config_dir / "dialects"
        if dialects_dir.exists():
            for ini_file in dialects_dir.glob("*.ini"):
                db_type = ini_file.stem  # filename without extension
                try:
                    # Merge with existing config or create new one
                    dialect_config = self._parse_ini(ini_file)
                    if db_type in self.configs:
                        # Merge: dialect config takes precedence
                        self.configs[db_type].update(dialect_config)
                        logger.info(f"✓ Merged dialect config: {db_type}")
                    else:
                        self.configs[db_type] = dialect_config
                        logger.info(f"✓ Loaded dialect config: {db_type}")
                except Exception as e:
                    logger.error(f"✗ Failed to load dialect config {db_type}: {e}")
    
    def _parse_ini(self, ini_path: Path) -> Dict:
        """Parse INI file with robust error handling
        
        Tolerates:
        - Duplicate keys (uses last value)
        - Missing sections
        - Malformed lines
        """
        # Use strict=False to allow duplicate keys (uses last value)
        config = configparser.ConfigParser(
            allow_no_value=True,
            strict=False  # Allow duplicate keys - uses last value
        )
        
        try:
            config.read(ini_path, encoding='utf-8')
            logger.debug(f"✓ Parsed INI file: {ini_path}")
        except configparser.DuplicateOptionError as e:
            logger.warning(f"⚠️  Duplicate option in {ini_path}: {e} (using last value)")
        except configparser.DuplicateSectionError as e:
            logger.warning(f"⚠️  Duplicate section in {ini_path}: {e}")
        except Exception as e:
            logger.error(f"✗ Error parsing {ini_path}: {e}")
            return {}
        
        result = {}
        for section in config.sections():
            try:
                result[section] = dict(config.items(section))
            except Exception as e:
                logger.warning(f"⚠️  Error reading section [{section}] from {ini_path}: {e}")
                result[section] = {}
        
        return result
    
    def get_config(self, database_type: str) -> Optional[Dict]:
        """Get configuration for a specific database type"""
        return self.configs.get(database_type)
    
    def get_dialect_instructions(self, database_type: str) -> str:
        """Get dialect-specific prompt instructions for SQL generation
        
        Tries multiple locations:
        1. backend/config/dialects/{database_type}.ini [dialect] prompt_snippet
        2. backend/config/{database_type}.ini [dialect] prompt_snippet
        3. backend/config/{database_type}.ini [dialect] prompt_instructions (legacy)
        """
        # Try new dialects/ directory first
        dialect_path = self.config_dir / "dialects" / f"{database_type.lower()}.ini"
        
        if dialect_path.exists():
            try:
                config = configparser.ConfigParser(allow_no_value=True, strict=False)
                config.read(dialect_path, encoding='utf-8')
                
                if 'dialect' in config:
                    # Try prompt_snippet first (new format)
                    if 'prompt_snippet' in config['dialect']:
                        instructions = config['dialect']['prompt_snippet']
                        logger.info(f"✓ Loaded dialect instructions from {dialect_path}")
                        return instructions
                    
                    # Fall back to prompt_instructions (legacy format)
                    if 'prompt_instructions' in config['dialect']:
                        instructions = config['dialect']['prompt_instructions']
                        logger.info(f"✓ Loaded dialect instructions (legacy) from {dialect_path}")
                        return instructions
            except Exception as e:
                logger.warning(f"⚠️  Error reading dialect instructions from {dialect_path}: {e}")
        
        # Fall back to old location in main config
        config = self.get_config(database_type)
        if not config:
            logger.warning(f"⚠️  No config found for database type: {database_type}")
            return ""
        
        dialect_config = config.get('dialect', {})
        instructions = dialect_config.get('prompt_snippet', '') or dialect_config.get('prompt_instructions', '')
        
        if instructions:
            logger.info(f"✓ Loaded dialect instructions from main config for {database_type}")
        else:
            logger.warning(f"⚠️  No dialect instructions found for {database_type}")
        
        return instructions
    
    def get_connection_string(self, database_type: str) -> Optional[str]:
        """Get connection string for a database type"""
        config = self.get_config(database_type)
        if not config:
            return None
        
        db_config = config.get(database_type, {})
        
        if database_type == "snowflake":
            host = db_config.get("host", "").split(".")[0]  # Extract account ID
            user = db_config.get("username", "")
            password = db_config.get("password", "")
            database = db_config.get("database", "")
            warehouse = db_config.get("warehouse", "COMPUTE_WH")
            role = db_config.get("role", "ACCOUNTADMIN")
            
            return (
                f"snowflake://{user}:{password}@{host}/{database}"
                f"?warehouse={warehouse}&role={role}"
            )
        
        elif database_type == "sqlserver":
            host = db_config.get("host", "localhost")
            database = db_config.get("database", "")
            user = db_config.get("username", "")
            password = db_config.get("password", "")
            auth_type = db_config.get("auth_type", "sql")
            driver = db_config.get("driver", "ODBC Driver 17 for SQL Server")
            
            if auth_type == "windows":
                return (
                    f"mssql+pyodbc://@{host}/{database}?"
                    f"driver={driver}&trusted_connection=yes"
                )
            else:
                return (
                    f"mssql+pyodbc://{user}:{password}@{host}/{database}?"
                    f"driver={driver}"
                )
        
        elif database_type == "postgres":
            host = db_config.get("host", "localhost")
            port = db_config.get("port", "5432")
            database = db_config.get("database", "postgres")
            user = db_config.get("username", "postgres")
            password = db_config.get("password", "")
            
            return (
                f"postgresql://{user}:{password}@{host}:{port}/{database}"
            )
        
        elif database_type == "redshift":
            host = db_config.get("host", "")
            port = db_config.get("port", "5439")
            database = db_config.get("database", "dev")
            user = db_config.get("username", "")
            password = db_config.get("password", "")
            
            return (
                f"redshift+psycopg2://{user}:{password}@{host}:{port}/{database}"
            )
        
        elif database_type == "bigquery":
            project_id = db_config.get("project_id", "")
            return f"bigquery://{project_id}"
        
        return None
    
    def list_available_databases(self) -> list:
        """List all available database configurations"""
        return list(self.configs.keys())


# Global config loader instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get or create global config loader"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def load_database_config(database_type: str) -> Optional[Dict]:
    """Load configuration for a specific database"""
    loader = get_config_loader()
    return loader.get_config(database_type)

def get_connection_string(database_type: str) -> Optional[str]:
    """Get connection string for a database type"""
    loader = get_config_loader()
    return loader.get_connection_string(database_type)

