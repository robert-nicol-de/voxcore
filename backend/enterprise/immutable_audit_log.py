"""
STEP 16.4 — AUDIT LOG (IMMUTABLE)

Tamper-evident audit logging using hash chaining.

Each log entry contains:
- Event details
- Hash of current entry
- Hash of previous entry (creates chain)

If someone tries to modify a log entry, the chain breaks
and it becomes immediately obvious.

Hash structure:
  hash = SHA256(previous_hash + timestamp + event + user + action)

Verification:
  current_entry.hash == SHA256(previous_entry.hash + current_entry.data)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import hashlib
import json
from abc import ABC, abstractmethod


class AuditEventType(str, Enum):
    """Types of auditable events"""
    # Access events
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    QUERY_EXECUTED = "query_executed"
    REPORT_GENERATED = "report_generated"
    
    # Admin events
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    
    # Security events
    AUTH_FAILED = "auth_failed"
    RATE_LIMIT_HIT = "rate_limit_hit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ENCRYPTION_KEY_ROTATED = "encryption_key_rotated"
    SECRET_ACCESSED = "secret_accessed"
    
    # Data events
    DATA_EXPORTED = "data_exported"
    DATA_DELETED = "data_deleted"
    DATA_MODIFIED = "data_modified"
    SCHEMA_CHANGED = "schema_changed"
    
    # System events
    BACKUP_COMPLETED = "backup_completed"
    RESTORE_COMPLETED = "restore_completed"
    ALERT_TRIGGERED = "alert_triggered"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class AuditLogEntry:
    """Single audit log entry in hash chain"""
    
    id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    
    # Hash chain
    entry_hash: str = ""
    previous_hash: str = ""
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for hashing and storage"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "details": self.details,
            "ip_address": self.ip_address,
            "success": self.success,
            "error_message": self.error_message
        }
    
    def calculate_hash(self) -> str:
        """Calculate SHA256 hash of this entry"""
        # Combine previous hash + this entry's data
        data = self.previous_hash + json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self) -> bool:
        """Verify hash chain integrity"""
        calculated = self.calculate_hash()
        return calculated == self.entry_hash


class ImmutableAuditLog(ABC):
    """Abstract immutable audit log"""
    
    @abstractmethod
    async def log_event(self, event: AuditLogEntry) -> str:
        """Record audit event and return entry ID"""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[AuditLogEntry]:
        """Retrieve audit event by ID"""
        pass
    
    @abstractmethod
    async def list_events(self, user_id: Optional[str] = None, 
                         event_type: Optional[AuditEventType] = None,
                         limit: int = 100) -> List[AuditLogEntry]:
        """List audit events with optional filters"""
        pass
    
    @abstractmethod
    async def verify_chain(self, start_id: Optional[str] = None, 
                          end_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify hash chain integrity in range"""
        pass


class InMemoryAuditLog(ImmutableAuditLog):
    """
    In-memory immutable audit log (for development).
    Production should use database-backed implementation.
    """
    
    def __init__(self):
        self.entries: Dict[str, AuditLogEntry] = {}
        self.entry_sequence: List[str] = []  # Track insertion order
        self.last_hash = ""
    
    async def log_event(self, event: AuditLogEntry) -> str:
        """Log event with hash chaining"""
        # Set the previous hash
        event.previous_hash = self.last_hash
        
        # Calculate hash
        event.entry_hash = event.calculate_hash()
        
        # Store
        self.entries[event.id] = event
        self.entry_sequence.append(event.id)
        self.last_hash = event.entry_hash
        
        return event.id
    
    async def get_event(self, event_id: str) -> Optional[AuditLogEntry]:
        """Get event by ID"""
        return self.entries.get(event_id)
    
    async def list_events(self, user_id: Optional[str] = None,
                         event_type: Optional[AuditEventType] = None,
                         limit: int = 100) -> List[AuditLogEntry]:
        """List events with filters"""
        results = []
        
        # Iterate in reverse to get most recent first
        for entry_id in reversed(self.entry_sequence[-limit:]):
            entry = self.entries[entry_id]
            
            if user_id and entry.user_id != user_id:
                continue
            if event_type and entry.event_type != event_type:
                continue
            
            results.append(entry)
        
        return results
    
    async def verify_chain(self, start_id: Optional[str] = None,
                          end_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify hash chain integrity"""
        results = {
            "total_entries": len(self.entries),
            "verified_entries": 0,
            "failed_entries": 0,
            "failures": []
        }
        
        ids_to_check = self.entry_sequence
        if start_id:
            start_idx = self.entry_sequence.index(start_id) if start_id in self.entry_sequence else 0
            ids_to_check = ids_to_check[start_idx:]
        
        if end_id:
            end_idx = self.entry_sequence.index(end_id) if end_id in self.entry_sequence else len(ids_to_check)
            ids_to_check = ids_to_check[:end_idx + 1]
        
        prev_hash = ""
        for entry_id in ids_to_check:
            entry = self.entries[entry_id]
            
            # Check that previous hash matches
            if entry.previous_hash != prev_hash:
                results["failed_entries"] += 1
                results["failures"].append({
                    "entry_id": entry_id,
                    "reason": "previous_hash_mismatch",
                    "expected": prev_hash,
                    "actual": entry.previous_hash
                })
            elif not entry.verify_hash():
                results["failed_entries"] += 1
                results["failures"].append({
                    "entry_id": entry_id,
                    "reason": "hash_verification_failed",
                    "stored_hash": entry.entry_hash,
                    "calculated_hash": entry.calculate_hash()
                })
            else:
                results["verified_entries"] += 1
            
            prev_hash = entry.entry_hash
        
        results["chain_integrity"] = results["failed_entries"] == 0
        return results
    
    def get_stats(self) -> dict:
        """Get audit log statistics"""
        event_counts = {}
        for entry in self.entries.values():
            event_type = entry.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "event_types": event_counts,
            "last_hash": self.last_hash
        }


# Global audit log instance
_audit_log = None


async def get_audit_log() -> ImmutableAuditLog:
    """Get or create global audit log"""
    global _audit_log
    if _audit_log is None:
        _audit_log = InMemoryAuditLog()
    return _audit_log


# Convenience logging functions
async def log_data_access(user_id: str, resource: str, columns: List[str],
                         ip_address: Optional[str] = None, success: bool = True):
    """Log data access event"""
    import uuid
    import time
    
    audit_log = await get_audit_log()
    entry = AuditLogEntry(
        id=str(uuid.uuid4()),
        event_type=AuditEventType.DATA_ACCESS,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        action="select",
        resource=resource,
        details={"columns": columns},
        ip_address=ip_address,
        success=success
    )
    return await audit_log.log_event(entry)


async def log_query_executed(user_id: str, query: str, execution_time_ms: float,
                            rows_returned: int, ip_address: Optional[str] = None,
                            success: bool = True, error: Optional[str] = None):
    """Log query execution event"""
    import uuid
    
    audit_log = await get_audit_log()
    entry = AuditLogEntry(
        id=str(uuid.uuid4()),
        event_type=AuditEventType.QUERY_EXECUTED,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        action="query",
        resource="database",
        details={
            "query_length": len(query),
            "execution_time_ms": execution_time_ms,
            "rows_returned": rows_returned
        },
        ip_address=ip_address,
        success=success,
        error_message=error
    )
    return await audit_log.log_event(entry)


async def log_auth_event(user_id: str, event_type: AuditEventType, ip_address: str,
                        success: bool = True, error: Optional[str] = None):
    """Log authentication event"""
    import uuid
    
    audit_log = await get_audit_log()
    entry = AuditLogEntry(
        id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        action="auth",
        resource="authentication",
        ip_address=ip_address,
        success=success,
        error_message=error
    )
    return await audit_log.log_event(entry)
