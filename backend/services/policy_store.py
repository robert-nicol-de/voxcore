"""
Policy Store: Persistence layer for data policies

Loads, saves, and manages policies from file or database.
Organizes policies by organization (multi-tenant support).
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.policy_definition import PolicyDefinition, PolicySet, PolicyType


class PolicyStore:
    """
    Persist and retrieve data policies.
    
    Supports:
    - File-based storage (JSON)
    - In-memory cache
    - Per-organization policy sets
    """
    
    def __init__(self, storage_path: str = "data/policies"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, PolicySet] = {}
    
    def get_org_policy_set(self, org_id: str, load_from_disk: bool = True) -> PolicySet:
        """Get policy set for organization (from cache or disk)"""
        # Check cache first
        if org_id in self.cache:
            return self.cache[org_id]
        
        # Try to load from disk
        if load_from_disk:
            policy_set = self.load_from_file(org_id)
            if policy_set:
                self.cache[org_id] = policy_set
                return policy_set
        
        # Return empty set
        policy_set = PolicySet(org_id=org_id)
        self.cache[org_id] = policy_set
        return policy_set
    
    def save_policy(self, org_id: str, policy: PolicyDefinition) -> None:
        """Add policy and persist"""
        policy_set = self.get_org_policy_set(org_id, load_from_disk=False)
        policy_set.add_policy(policy)
        self.save_to_file(org_id, policy_set)
    
    def delete_policy(self, org_id: str, policy_name: str) -> bool:
        """Remove policy and persist"""
        policy_set = self.get_org_policy_set(org_id)
        removed = policy_set.remove_policy(policy_name)
        if removed:
            self.save_to_file(org_id, policy_set)
        return removed
    
    def update_policy(self, org_id: str, policy: PolicyDefinition) -> None:
        """Update existing policy"""
        policy_set = self.get_org_policy_set(org_id)
        # Remove old, add new
        policy_set.remove_policy(policy.name)
        policy_set.add_policy(policy)
        self.save_to_file(org_id, policy_set)
    
    def get_all_policies(self, org_id: str) -> List[PolicyDefinition]:
        """Get all policies for organization"""
        policy_set = self.get_org_policy_set(org_id)
        return policy_set.policies
    
    def get_policy(self, org_id: str, policy_name: str) -> Optional[PolicyDefinition]:
        """Get single policy by name"""
        policy_set = self.get_org_policy_set(org_id)
        for policy in policy_set.policies:
            if policy.name == policy_name:
                return policy
        return None
    
    def clear_cache(self, org_id: Optional[str] = None) -> None:
        """Clear in-memory cache"""
        if org_id:
            self.cache.pop(org_id, None)
        else:
            self.cache.clear()
    
    def save_to_file(self, org_id: str, policy_set: PolicySet) -> None:
        """Persist policy set to JSON file"""
        org_dir = self.storage_path / org_id
        org_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = org_dir / "policies.json"
        
        # Convert to dict
        data = {
            "org_id": org_id,
            "updated_at": datetime.now().isoformat(),
            "policies": [p.to_dict() for p in policy_set.policies]
        }
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_from_file(self, org_id: str) -> Optional[PolicySet]:
        """Load policy set from JSON file"""
        file_path = self.storage_path / org_id / "policies.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            policy_set = PolicySet(org_id=org_id)
            
            for policy_data in data.get("policies", []):
                try:
                    policy = PolicyDefinition.from_dict(policy_data)
                    policy_set.add_policy(policy)
                except Exception as e:
                    print(f"Warning: Failed to load policy {policy_data.get('name', 'unknown')}: {e}")
            
            return policy_set
        
        except Exception as e:
            print(f"Error loading policies for {org_id}: {e}")
            return None
    
    def export_org_policies(self, org_id: str, output_file: str) -> None:
        """Export all org policies to file"""
        policy_set = self.get_org_policy_set(org_id)
        
        data = {
            "org_id": org_id,
            "exported_at": datetime.now().isoformat(),
            "policies": [p.to_dict() for p in policy_set.policies]
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            if output_file.endswith('.json'):
                json.dump(data, f, indent=2, default=str)
            else:  # Assume YAML
                import yaml
                yaml.dump(data, f, default_flow_style=False)
    
    def import_org_policies(self, org_id: str, input_file: str, overwrite: bool = False) -> int:
        """
        Import policies from file.
        
        Args:
            org_id: Target organization
            input_file: Source file (JSON or YAML)
            overwrite: If True, clear existing policies first
        
        Returns:
            Number of policies imported
        """
        path = Path(input_file)
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {input_file}")
        
        # Load file
        with open(path, 'r') as f:
            if path.suffix == '.json':
                data = json.load(f)
            else:  # YAML
                import yaml
                data = yaml.safe_load(f)
        
        # Get or create policy set
        if overwrite:
            self.cache.pop(org_id, None)
        
        policy_set = self.get_org_policy_set(org_id, load_from_disk=False)
        
        # Import policies
        count = 0
        for policy_data in data.get("policies", []):
            try:
                policy = PolicyDefinition.from_dict(policy_data)
                # Remove if exists (update)
                policy_set.remove_policy(policy.name)
                policy_set.add_policy(policy)
                count += 1
            except Exception as e:
                print(f"Warning: Failed to import policy {policy_data.get('name', 'unknown')}: {e}")
        
        # Save to disk
        self.save_to_file(org_id, policy_set)
        
        return count
    
    def list_organizations(self) -> List[str]:
        """List all organizations with stored policies"""
        if not self.storage_path.exists():
            return []
        
        return [d.name for d in self.storage_path.iterdir() if d.is_dir()]
    
    def statistics(self, org_id: str) -> Dict[str, Any]:
        """Get statistics about policies"""
        policy_set = self.get_org_policy_set(org_id)
        
        type_counts = {}
        for policy in policy_set.policies:
            type_str = policy.type.value
            type_counts[type_str] = type_counts.get(type_str, 0) + 1
        
        return {
            "org_id": org_id,
            "total_policies": len(policy_set.policies),
            "enabled_policies": len([p for p in policy_set.policies if p.enabled]),
            "by_type": type_counts,
            "storage_path": str(self.storage_path / org_id)
        }


# Global store instance
_policy_store: Optional[PolicyStore] = None


def get_policy_store(storage_path: str = "data/policies") -> PolicyStore:
    """Get or create global policy store"""
    global _policy_store
    if _policy_store is None:
        _policy_store = PolicyStore(storage_path)
    return _policy_store


def initialize_policy_store(storage_path: str = "data/policies") -> None:
    """Initialize global policy store with custom path"""
    global _policy_store
    _policy_store = PolicyStore(storage_path)
