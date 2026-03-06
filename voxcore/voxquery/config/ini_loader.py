"""
INI-based dialect configuration loader
Reads dialect configs from .ini files and converts to DialectConfig objects
"""

import configparser
from pathlib import Path
from typing import Dict, Optional
from voxquery.config.dialects.dialect_config import DialectConfig


def parse_list(value: str) -> list:
    """Parse comma-separated list from INI value"""
    if not value:
        return []
    return [item.strip() for item in value.split(',')]


def parse_dict(section: Dict) -> dict:
    """Convert INI section to dictionary"""
    return dict(section)


def load_dialect_from_ini(ini_path: str) -> Optional[DialectConfig]:
    """Load dialect configuration from INI file"""
    config = configparser.ConfigParser()
    
    try:
        config.read(ini_path)
    except Exception as e:
        print(f"Error reading INI file {ini_path}: {e}")
        return None
    
    try:
        # Extract sections
        connection = dict(config['connection']) if 'connection' in config else {}
        dialect = dict(config['dialect']) if 'dialect' in config else {}
        prompt = dict(config['prompt']) if 'prompt' in config else {}
        schema_mapping = dict(config['schema_mapping']) if 'schema_mapping' in config else {}
        finance_keywords = dict(config['finance_keywords']) if 'finance_keywords' in config else {}
        whitelist_tables = dict(config['whitelist_tables']) if 'whitelist_tables' in config else {}
        forbidden_tables = dict(config['forbidden_tables']) if 'forbidden_tables' in config else {}
        validation = dict(config['validation']) if 'validation' in config else {}
        fallback_query = dict(config['fallback_query']) if 'fallback_query' in config else {}
        export = dict(config['export']) if 'export' in config else {}
        
        # Create DialectConfig object
        dialect_config = DialectConfig(
            name=dialect.get('name', 'unknown'),
            limit_syntax=dialect.get('limit_syntax', 'LIMIT'),
            top_position=dialect.get('top_position', 'end_of_query'),
            date_current=dialect.get('date_current', 'CURRENT_DATE()'),
            date_trunc=dialect.get('date_trunc', 'DATE_TRUNC'),
            date_add=dialect.get('date_add', 'DATE_ADD'),
            string_concat=dialect.get('string_concat', '||'),
            schema_separator=dialect.get('schema_separator', '.'),
            identifier_quote=dialect.get('identifier_quote', '"'),
            
            dialect_lock=prompt.get('dialect_lock', ''),
            forbidden_syntax=parse_list(prompt.get('forbidden_syntax', '')),
            required_syntax=parse_list(prompt.get('required_syntax', '')),
            top_format=prompt.get('top_format', 'SELECT TOP {n} ... ORDER BY column DESC'),
            date_format=prompt.get('date_format', ''),
            schema_required=prompt.get('schema_required', 'true').lower() == 'true',
            
            accounts_table=schema_mapping.get('accounts_table', 'ACCOUNTS'),
            accounts_balance_col=schema_mapping.get('accounts_balance_col', 'BALANCE'),
            accounts_name_col=schema_mapping.get('accounts_name_col', 'ACCOUNT_NAME'),
            accounts_id_col=schema_mapping.get('accounts_id_col', 'ACCOUNT_ID'),
            transactions_table=schema_mapping.get('transactions_table', 'TRANSACTIONS'),
            holdings_table=schema_mapping.get('holdings_table', 'HOLDINGS'),
            securities_table=schema_mapping.get('securities_table', 'SECURITIES'),
            security_prices_table=schema_mapping.get('security_prices_table', 'SECURITY_PRICES'),
            
            finance_keywords=finance_keywords,
            whitelist_tables=whitelist_tables,
            forbidden_tables=list(forbidden_tables.keys()),
            
            hard_reject_keywords=parse_list(validation.get('hard_reject_keywords', '')),
            score_threshold=float(validation.get('score_threshold', '0.7')),
            fallback_on_fail=validation.get('fallback_on_fail', 'true').lower() == 'true',
            
            fallback_sql=fallback_query.get('sql', ''),
            
            export_csv=export.get('csv', 'true').lower() == 'true',
            export_excel=export.get('excel', 'true').lower() == 'true',
            export_markdown=export.get('markdown', 'true').lower() == 'true',
            export_email=export.get('email', 'true').lower() == 'true',
            export_ssrs=export.get('ssrs', 'false').lower() == 'true',
        )
        
        return dialect_config
    
    except Exception as e:
        print(f"Error parsing INI file {ini_path}: {e}")
        return None


def load_all_dialects_from_directory(directory: str) -> Dict[str, DialectConfig]:
    """Load all dialect INI files from a directory"""
    dialects = {}
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Directory {directory} does not exist")
        return dialects
    
    for ini_file in dir_path.glob('*.ini'):
        dialect_config = load_dialect_from_ini(str(ini_file))
        if dialect_config:
            dialects[dialect_config.name] = dialect_config
            print(f"✅ Loaded dialect: {dialect_config.name} from {ini_file.name}")
    
    return dialects


# Load SQL Server config on module import
SQLSERVER_CONFIG_PATH = Path(__file__).parent / 'sqlserver.ini'
SQLSERVER_CONFIG_FROM_INI = load_dialect_from_ini(str(SQLSERVER_CONFIG_PATH))

if SQLSERVER_CONFIG_FROM_INI:
    print(f"✅ SQL Server dialect loaded from INI")
else:
    print(f"⚠️  Could not load SQL Server dialect from INI")
