"""
STEP 16.7 — ACCESS TRACEABILITY

Answer: "Who saw this data?"

Track every access to sensitive data:
- User ID
- Data element (column/field)
- Access time
- Whether masked/redacted
- Policy applied
- Result (granted/denied)

Enables:
- Forensic investigation
- Insider threat detection
- Compliance auditing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class AccessResult(str, Enum):
    """Result of access attempt"""
    GRANTED = "granted"          # User saw data
    GRANTED_MASKED = "masked"    # User saw masked data
    DENIED = "denied"            # Access blocked
    DENIED_APPROVAL = "denied_approval"  # Requires approval
    DENIED_ROLE = "denied_role"  # Role doesn't permit
    DENY_MFA = "denied_mfa"      # MFA required


@dataclass
class DataAccessRecord:
    """Record of single data access"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Who
    user_id: str = ""
    user_role: str = ""
    
    # What
    resource: str = ""  # table name
    column: str = ""    # field name
    classification: str = ""  # data sensitivity
    
    # How
    query_id: Optional[str] = None
    query_digest: Optional[str] = None  # Hashed query for pattern detection
    
    # Result
    result: AccessResult = AccessResult.GRANTED
    rows_accessed: int = 0
    data_masked: bool = False
    
    # Context
    ip_address: str = ""
    session_id: str = ""
    request_id: str = ""
    
    # Reason if denied
    denial_reason: Optional[str] = None
    
    # Policy applied
    policy_name: Optional[str] = None
    policy_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "user_role": self.user_role,
            "resource": self.resource,
            "column": self.column,
            "classification": self.classification,
            "query_id": self.query_id,
            "result": self.result.value,
            "rows_accessed": self.rows_accessed,
            "data_masked": self.data_masked,
            "ip_address": self.ip_address,
            "policy_name": self.policy_name
        }


class AccessTraceabilityLog:
    """
    Tracks all data access for forensic analysis.
    
    Storage: in-memory or database.
    For production, should use persistent database.
    """
    
    def __init__(self):
        self.records: Dict[str, DataAccessRecord] = {}
        self.access_index: Dict[str, List[str]] = {}  # user_id -> [record_ids]
    
    async def log_access(self, record: DataAccessRecord):
        """Log data access"""
        self.records[record.id] = record
        
        # Index by user for quick lookup
        if record.user_id not in self.access_index:
            self.access_index[record.user_id] = []
        self.access_index[record.user_id].append(record.id)
    
    async def get_user_access_history(self, user_id: str, limit: int = 100) -> List[DataAccessRecord]:
        """Get all access by user"""
        record_ids = self.access_index.get(user_id, [])
        
        # Return most recent
        records = [self.records[rid] for rid in record_ids[-limit:]]
        return sorted(records, key=lambda r: r.timestamp, reverse=True)
    
    async def get_column_access_history(self, resource: str, column: str, 
                                       limit: int = 100) -> List[DataAccessRecord]:
        """Get all access to specific column"""
        results = [r for r in self.records.values()
                   if r.resource == resource and r.column == column]
        
        # Sort by timestamp, most recent first
        results = sorted(results, key=lambda r: r.timestamp, reverse=True)
        return results[-limit:]
    
    async def find_suspicious_access(self, user_id: str, 
                                    minutes: int = 60) -> List[DataAccessRecord]:
        """Find suspicious access patterns"""
        
        user_records = await self.get_user_access_history(user_id, limit=10000)
        
        # Filter to recent timeframe
        cutoff = datetime.utcnow() - __import__('datetime').timedelta(minutes=minutes)
        recent = [r for r in user_records if r.timestamp >= cutoff]
        
        suspicious = []
        
        # Pattern 1: Many denied accesses
        denied_count = sum(1 for r in recent if r.result == AccessResult.DENIED)
        if denied_count > 5:
            suspicious.extend([r for r in recent if r.result == AccessResult.DENIED])
        
        # Pattern 2: Access to restricted data
        restricted_access = [r for r in recent 
                            if r.classification == "restricted"]
        if len(restricted_access) > 3:
            suspicious.extend(restricted_access)
        
        # Pattern 3: Access from unusual IP
        ips = set(r.ip_address for r in recent)
        if len(ips) > 5:
            # Multiple IPs in short time
            suspicious.extend([r for r in recent if r.result == AccessResult.GRANTED])
        
        return suspicious
    
    async def get_statistics(self, user_id: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> dict:
        """Get access statistics"""
        
        records_to_analyze = list(self.records.values())
        
        if user_id:
            records_to_analyze = [r for r in records_to_analyze 
                                 if r.user_id == user_id]
        
        if start_time:
            records_to_analyze = [r for r in records_to_analyze 
                                 if r.timestamp >= start_time]
        
        if end_time:
            records_to_analyze = [r for r in records_to_analyze 
                                 if r.timestamp <= end_time]
        
        # Calculate statistics
        result_counts = {}
        for result in AccessResult:
            count = sum(1 for r in records_to_analyze if r.result == result)
            result_counts[result.value] = count
        
        classification_counts = {}
        for record in records_to_analyze:
            c = record.classification
            classification_counts[c] = classification_counts.get(c, 0) + 1
        
        role_counts = {}
        for record in records_to_analyze:
            r = record.user_role
            role_counts[r] = role_counts.get(r, 0) + 1
        
        masked_count = sum(1 for r in records_to_analyze if r.data_masked)
        
        return {
            "total_accesses": len(records_to_analyze),
            "result_distribution": result_counts,
            "by_classification": classification_counts,
            "by_role": role_counts,
            "data_masked": masked_count,
            "data_unmasked": len(records_to_analyze) - masked_count,
            "approval_required": sum(1 for r in records_to_analyze 
                                    if r.result == AccessResult.DENIED_APPROVAL),
            "denied_total": sum(1 for r in records_to_analyze 
                               if "denied" in r.result.value)
        }


class AccessTraceabilityReport:
    """Generate reports from traceability log"""
    
    def __init__(self, log: AccessTraceabilityLog):
        self.log = log
    
    async def get_user_report(self, user_id: str) -> dict:
        """Get comprehensive report for user"""
        history = await self.log.get_user_access_history(user_id, limit=1000)
        
        return {
            "user_id": user_id,
            "total_accesses": len(history),
            "granted": sum(1 for r in history if r.result == AccessResult.GRANTED),
            "masked": sum(1 for r in history if r.result == AccessResult.GRANTED_MASKED),
            "denied": sum(1 for r in history if "denied" in r.result.value),
            "sensitive_accessed": sum(1 for r in history 
                                     if r.classification in ["sensitive", "restricted"]),
            "latest_access": history[0].timestamp.isoformat() if history else None,
            "access_history": [r.to_dict() for r in history[-10:]]  # Last 10
        }
    
    async def get_data_report(self, resource: str, column: str) -> dict:
        """Get report for specific data element"""
        history = await self.log.get_column_access_history(resource, column, limit=1000)
        
        unique_users = set(r.user_id for r in history)
        
        return {
            "resource": resource,
            "column": column,
            "total_accesses": len(history),
            "unique_users": len(unique_users),
            "users": list(unique_users),
            "granted": sum(1 for r in history if r.result == AccessResult.GRANTED),
            "masked": sum(1 for r in history if r.result == AccessResult.GRANTED_MASKED),
            "denied": sum(1 for r in history if "denied" in r.result.value),
            "recent_access": [r.to_dict() for r in history[-5:]]
        }


# Global traceability log
_traceability_log = None


async def get_traceability_log() -> AccessTraceabilityLog:
    """Get or create global log"""
    global _traceability_log
    if _traceability_log is None:
        _traceability_log = AccessTraceabilityLog()
    return _traceability_log


async def log_data_access(user_id: str, resource: str, column: str, 
                         classification: str, user_role: str,
                         result: AccessResult, ip_address: str,
                         rows_accessed: int = 0, data_masked: bool = False,
                         policy_name: Optional[str] = None):
    """Convenience function: log data access"""
    
    log = await get_traceability_log()
    record = DataAccessRecord(
        user_id=user_id,
        user_role=user_role,
        resource=resource,
        column=column,
        classification=classification,
        result=result,
        rows_accessed=rows_accessed,
        data_masked=data_masked,
        ip_address=ip_address,
        policy_name=policy_name
    )
    
    await log.log_access(record)
