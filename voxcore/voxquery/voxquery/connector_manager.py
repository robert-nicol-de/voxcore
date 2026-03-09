import configparser
import os
import json
from typing import List, Dict, Any, Optional

# Get absolute path to project root
# Script is at: voxcore/voxquery/voxquery/connector_manager.py
# Project root is 3 levels up
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONNECTOR_FOLDER = os.path.join(PROJECT_ROOT, "connectors")
TENANTS_FOLDER = os.path.join(PROJECT_ROOT, "voxcore", "tenants")

def load_connectors(tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load all database connectors for a specific tenant or globally.
    
    Multi-tenant architecture:
    - If tenant_id is provided: Load from tenants/{tenant_id}/connectors/
    - If tenant_id is None: Load from legacy connectors/ folder (backward compatible)
    
    Each .ini file represents a database configuration.
    
    Credentials are loaded from:
    1. Environment variables (via credential_key in .ini)
    2. Falls back to graceful error if credential not found
    
    Security policies are defined in the [security] section of each .ini file.
    """
    connectors = []
    
    # Determine connector folder based on tenant_id
    if tenant_id:
        connector_folder = os.path.join(TENANTS_FOLDER, tenant_id, "connectors")
    else:
        connector_folder = CONNECTOR_FOLDER

    if not os.path.exists(connector_folder):
        if tenant_id:
            print(f"Warning: Connector folder not found for tenant '{tenant_id}'")
        return connectors

    for file in os.listdir(connector_folder):
        if file.endswith(".ini"):
            try:
                config = configparser.ConfigParser()
                config.read(os.path.join(connector_folder, file))

                if "database" in config:
                    db = config["database"]
                    
                    # Get credential key from .ini and lookup actual password from environment
                    credential_key = db.get("credential_key")
                    password = None
                    credential_status = "missing"
                    
                    if credential_key:
                        password = os.getenv(credential_key)
                        if password:
                            credential_status = "loaded"
                        else:
                            credential_status = "not_found"
                            print(f"Warning: Credential '{credential_key}' not found in environment for connector {db.get('name')}")
                    
                    connector = {
                        "name": db.get("name", file.replace(".ini", "")),
                        "type": db.get("type", "unknown"),
                        "host": db.get("host", ""),
                        "port": int(db.get("port", 0)) if db.get("port") else None,
                        "database": db.get("database", ""),
                        "user": db.get("user", ""),
                        "password": password,  # Loaded from environment, None if not found
                        "credential_key": credential_key,
                        "credential_status": credential_status,  # loaded, not_found, or missing
                        "status": "connected" if password else "error",
                        "tenant_id": tenant_id or "default"
                    }

                    # Load security policies if available
                    if "security" in config:
                        security = config["security"]
                        connector["security"] = {
                            "block_delete": security.getboolean("block_delete", False),
                            "block_update": security.getboolean("block_update", False),
                            "block_drop": security.getboolean("block_drop", False),
                            "max_rows": int(security.get("max_rows", 10000)),
                            "protect_tables": [t.strip() for t in security.get("protect_tables", "").split(",") if t.strip()],
                            "pii_protected": security.getboolean("pii_protected", False),
                            "policy": security.get("policy", None)
                        }
                    else:
                        connector["security"] = {
                            "block_delete": False,
                            "block_update": False,
                            "block_drop": False,
                            "max_rows": 10000,
                            "protect_tables": [],
                            "pii_protected": False,
                            "policy": None
                        }

                    connectors.append(connector)

            except Exception as e:
                print(f"Error loading connector {file}: {e}")

    return connectors


def get_connector_by_name(name: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific connector by name for a tenant."""
    connectors = load_connectors(tenant_id=tenant_id)
    for connector in connectors:
        if connector["name"] == name:
            return connector
    return None


def load_tenant_config(tenant_id: str) -> Optional[Dict[str, Any]]:
    """Load tenant configuration (users, policies, metadata)."""
    tenant_folder = os.path.join(TENANTS_FOLDER, tenant_id)
    
    if not os.path.exists(tenant_folder):
        return None
    
    config = {
        "tenant_id": tenant_id,
        "users": [],
        "policies": {}
    }
    
    # Load users.json
    users_file = os.path.join(tenant_folder, "users.json")
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users_data = json.load(f)
                config.update(users_data)
        except Exception as e:
            print(f"Error loading users for tenant {tenant_id}: {e}")
    
    # Load policies.ini
    policies_file = os.path.join(tenant_folder, "policies.ini")
    if os.path.exists(policies_file):
        try:
            policy_config = configparser.ConfigParser()
            policy_config.read(policies_file)
            
            for section in policy_config.sections():
                config["policies"][section] = dict(policy_config[section])
        except Exception as e:
            print(f"Error loading policies for tenant {tenant_id}: {e}")
    
    return config


def get_tenant_user(tenant_id: str, user_email: str) -> Optional[Dict[str, Any]]:
    """Get a specific user for a tenant."""
    config = load_tenant_config(tenant_id)
    if not config:
        return None
    
    for user in config.get("users", []):
        if user["email"] == user_email:
            return user
    
    return None


def list_all_tenants() -> List[str]:
    """List all available tenant IDs."""
    tenants = []
    
    if not os.path.exists(TENANTS_FOLDER):
        return tenants
    
    for item in os.listdir(TENANTS_FOLDER):
        item_path = os.path.join(TENANTS_FOLDER, item)
        if os.path.isdir(item_path):
            tenants.append(item)
    
    return sorted(tenants)

    return None


def get_connector_count() -> int:
    """Get the total number of available connectors."""
    return len(load_connectors())
