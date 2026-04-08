"""
TenantConnectionManager - Per-Org Database Connection Pooling

Each organization can have:
- Separate database instance (hard isolation)
- Separate schema in shared database
- Separate credentials

This manager maintains a connection pool per org_id.

Usage:
  manager = TenantConnectionManager()
  
  # Register org's database connection
  manager.register_org_connection(
      org_id="acme_corp",
      host="acme-db.example.com",
      port=5432,
      database="acme_data",
      username="acme_user",
      password="..."
  )
  
  # Get connection for org (auto-pools)
  conn = manager.get_connection(org_id="acme_corp")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM customers")
"""

import os
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import psycopg2
from psycopg2 import pool as pg_pool
from .tenant_context import require_context, get_org_id

# Default connection pool size per org
DEFAULT_POOL_MIN_SIZE = 2
DEFAULT_POOL_MAX_SIZE = 10


@dataclass
class OrgConnectionConfig:
    """Database connection config for an organization"""

    org_id: str
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: Optional[str] = None  # PostgreSQL schema (optional)
    options: Optional[Dict[str, str]] = None  # Extra connection options

    def get_connection_string(self) -> str:
        """Build PostgreSQL connection string"""
        cs = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        if self.schema:
            cs += f"?options=-c%20search_path={self.schema}"
        return cs


class TenantConnectionManager:
    """
    Manages per-tenant database connections.

    Thread-safe singleton for managing organization-specific database pools.
    """

    def __init__(self):
        self._connection_pools: Dict[str, pg_pool.SimpleConnectionPool] = {}
        self._org_configs: Dict[str, OrgConnectionConfig] = {}
        self._lock = threading.RLock()

    def register_org_connection(
        self,
        org_id: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        schema: Optional[str] = None,
    ) -> bool:
        """
        Register a database connection for an organization.

        Args:
            org_id: Organization identifier
            host: Database host
            port: Database port
            database: Database name
            username: Connection username
            password: Connection password
            schema: PostgreSQL schema (optional, for schema isolation)

        Returns:
            True if registered successfully

        Raises:
            ValueError: If org_id is empty
            psycopg2.Error: If connection cannot be established
        """
        if not org_id:
            raise ValueError("org_id is required")

        with self._lock:
            # Test connection before registering
            try:
                test_conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    connect_timeout=5,
                )
                test_conn.close()
            except psycopg2.Error as e:
                raise ValueError(f"Cannot connect to database for {org_id}: {e}")

            # Store config
            config = OrgConnectionConfig(
                org_id=org_id,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                schema=schema,
            )
            self._org_configs[org_id] = config

            # Create connection pool
            self._connection_pools[org_id] = pg_pool.SimpleConnectionPool(
                DEFAULT_POOL_MIN_SIZE,
                DEFAULT_POOL_MAX_SIZE,
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
            )

            return True

    def get_connection(self, org_id: Optional[str] = None):
        """
        Get a database connection for an organization.

        If org_id not provided, uses current tenant context.

        Args:
            org_id: Organization ID (optional, uses context if not provided)

        Returns:
            psycopg2 connection object

        Raises:
            RuntimeError: If org not registered or no tenant context
            pool.PoolError: If connection pool exhausted
        """
        if not org_id:
            org_id = get_org_id()  # Raises if no context

        with self._lock:
            if org_id not in self._connection_pools:
                raise RuntimeError(
                    f"No database connection configured for org: {org_id}. "
                    f"Call register_org_connection() first."
                )

            conn = self._connection_pools[org_id].getconn()

            # Set schema if configured (PostgreSQL)
            config = self._org_configs.get(org_id)
            if config and config.schema:
                cursor = conn.cursor()
                cursor.execute(f"SET search_path TO {config.schema}")
                cursor.close()
                conn.commit()

            return conn

    def return_connection(self, conn, org_id: Optional[str] = None):
        """
        Return a connection to the pool.

        Args:
            conn: Connection object to return
            org_id: Organization ID (optional, uses context if not provided)
        """
        if not org_id:
            org_id = get_org_id()

        with self._lock:
            if org_id not in self._connection_pools:
                conn.close()
                return

            try:
                self._connection_pools[org_id].putconn(conn)
            except Exception:
                conn.close()

    def close_org_pool(self, org_id: str) -> bool:
        """
        Close all connections for an organization (e.g., on deprovisioning).

        Args:
            org_id: Organization ID

        Returns:
            True if pool existed and was closed
        """
        with self._lock:
            if org_id not in self._connection_pools:
                return False

            try:
                self._connection_pools[org_id].closeall()
            except Exception:
                pass

            del self._connection_pools[org_id]
            if org_id in self._org_configs:
                del self._org_configs[org_id]

            return True

    def get_pool_stats(self, org_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get connection pool statistics for an organization.

        Args:
            org_id: Organization ID (optional, uses context if not provided)

        Returns:
            Dictionary with pool statistics
        """
        if not org_id:
            org_id = get_org_id()

        with self._lock:
            pool = self._connection_pools.get(org_id)
            if not pool:
                return {"available": 0, "used": 0}

            return {
                "available": pool._pool_size,
                "used": pool._pool_size - len(pool._queue),
            }

    def get_all_registered_orgs(self) -> list:
        """Get list of all registered organization IDs"""
        with self._lock:
            return list(self._org_configs.keys())


# Singleton instance
_manager: Optional[TenantConnectionManager] = None


def get_tenant_connection_manager() -> TenantConnectionManager:
    """Get or create global TenantConnectionManager instance"""
    global _manager
    if _manager is None:
        _manager = TenantConnectionManager()
    return _manager


# Helper function for use in query execution
def get_org_connection(org_id: Optional[str] = None):
    """
    Get a database connection for the current or specified organization.

    Convenience function that combines context + manager.

    Args:
        org_id: Organization ID (optional, uses context if not provided)

    Returns:
        psycopg2 connection object

    Usage:
        from backend.services.tenant_context import tenant_context
        from backend.services.tenant_connection_manager import get_org_connection
        
        with tenant_context(org_id="acme_corp"):
            conn = get_org_connection()  # Automatically for acme_corp
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers")
    """
    manager = get_tenant_connection_manager()
    return manager.get_connection(org_id)
