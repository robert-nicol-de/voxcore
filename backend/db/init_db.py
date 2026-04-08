"""
Initialize database schema.

Run this once to create all tables:
  python backend/db/init_db.py

This script:
1. Reads all SQL migration files from db/migrations/
2. Connects to database (using DATABASE_URL from .env)
3. Executes migrations in order
4. Reports success/failure
"""

import os
import sys
from pathlib import Path

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """
    Get DATABASE_URL from environment.
    Falls back to SQLite for local dev.
    """
    url = os.getenv('DATABASE_URL')
    
    if not url:
        logger.warning("DATABASE_URL not set, using SQLite")
        url = 'sqlite:///voxcore.db'
    
    return url

def get_connection():
    """Get database connection based on DATABASE_URL"""
    db_url = get_database_url()
    logger.info(f"Connecting to: {db_url.split('://')[0]}://...")
    
    if db_url.startswith('sqlite'):
        # SQLite connection
        import sqlite3
        db_path = db_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.isolation_level = None
        return conn, 'sqlite'
    
    elif db_url.startswith('postgresql'):
        # PostgreSQL connection
        import psycopg2
        try:
            conn = psycopg2.connect(db_url)
            conn.autocommit = True
            return conn, 'postgresql'
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    else:
        raise ValueError(f"Unsupported database: {db_url}")

def run_migration(conn, sql_content, migration_name):
    """
    Execute a single migration.
    Handles both SQLite and PostgreSQL.
    """
    try:
        cursor = conn.cursor()
        
        # For SQLite, need to handle differently
        if cursor.connection.__class__.__name__ == 'Connection':  # SQLite
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
        else:  # PostgreSQL
            cursor.execute(sql_content)
        
        logger.info(f"✅ {migration_name}")
        return True
    
    except Exception as e:
        logger.error(f"❌ {migration_name}: {e}")
        return False

def main():
    """Run all migrations"""
    
    logger.info("=" * 50)
    logger.info("VoxCore Database Initialization")
    logger.info("=" * 50)
    logger.info("")
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # Get connection
    try:
        conn, db_type = get_connection()
        logger.info(f"✅ Connected to {db_type}")
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False
    
    logger.info("")
    logger.info("Running migrations...")
    logger.info("")
    
    # Get all migration files
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        logger.warning("No migrations found")
        return True
    
    # Run each migration
    success_count = 0
    for migration_file in migration_files:
        with open(migration_file, 'r') as f:
            sql_content = f.read()
        
        # Skip comments and empty lines at the start
        sql_content = '\n'.join(
            line for line in sql_content.split('\n')
            if not line.strip().startswith('--')
        )
        
        if run_migration(conn, sql_content, migration_file.name):
            success_count += 1
    
    # Close connection
    conn.close()
    
    logger.info("")
    logger.info("=" * 50)
    logger.info(f"Completed: {success_count}/{len(migration_files)} migrations successful")
    logger.info("=" * 50)
    
    if success_count == len(migration_files):
        logger.info("")
        logger.info("✨ Database ready for production!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Start backend: python -m uvicorn voxcore.api.playground_api:app --reload")
        logger.info("  2. Execute a query through the UI")
        logger.info("  3. Verify audit logs stored: SELECT COUNT(*) FROM query_logs;")
        logger.info("")
        return True
    else:
        logger.error("Some migrations failed. Fix errors above and try again.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
