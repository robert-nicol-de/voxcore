"""
STEP 8 — Data Policy Engine: Policy Definition System

Defines the data structures for expressing and managing fine-grained data access policies.
This is your core product moat - controlling who sees what at data level.

Policy Types:
- MASK: Replace sensitive values with *** (column-level)
- REDACT: Remove column entirely from results
- FILTER: Add WHERE clause for row-level filtering
- AGGREGATE_ONLY: Allow only aggregated queries (COUNT, SUM, AVG)
- BLOCK: Deny access entirely

Policy Conditions:
- role: User job role (analyst, admin, executive, etc.)
- user_id: Specific user ID
- column: Column to apply policy on
- row_condition: Row-level WHERE clause condition
- time_window: Restrict access to specific time windows
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import time


class PolicyType(str, Enum):
    """Supported policy types"""
    MASK = "mask"
    REDACT = "redact"
    FILTER = "filter"
    AGGREGATE_ONLY = "aggregate_only"
    BLOCK = "block"


class ConditionOperator(str, Enum):
    """Operators for policy conditions"""
    EQUALS = "equals"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    REGEX = "regex"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


@dataclass
class TimeWindow:
    """Define time range when policy applies"""
    start_time: time  # HH:MM format
    end_time: time
    days_of_week: Optional[List[str]] = None  # ["MON", "TUE", ...] or None for all days
    
    def is_active(self) -> bool:
        """Check if current time falls within window"""
        from datetime import datetime
        now = datetime.now().time()
        if self.days_of_week:
            current_day = datetime.now().strftime("%a").upper()
            if current_day not in self.days_of_week:
                return False
        return self.start_time <= now <= self.end_time


@dataclass
class PolicyCondition:
    """
    Condition that must be TRUE for policy to apply.
    
    Examples:
    - role="analyst" - applies when user's role is analyst
    - user_id="acme_user_123" - applies to specific user
    - column="salary" - applies to salary column
    - row_condition="department_id = 5" - applies to specific rows
    """
    
    # WHO: User attributes
    role: Optional[str] = None  # e.g., "analyst", "manager", "executive"
    user_id: Optional[str] = None
    user_attribute: Optional[Dict[str, Any]] = None  # e.g., {"department": "engineering"}
    
    # WHAT: Data attributes
    column: Optional[str] = None
    table: Optional[str] = None
    
    # WHEN: Data-level conditions
    row_condition: Optional[str] = None  # Raw WHERE clause, e.g., "salary > 100000"
    time_window: Optional[TimeWindow] = None
    
    # HOW: Logical operators for multiple conditions
    operator: str = "AND"  # "AND" or "OR"
    
    def __post_init__(self):
        """Validate condition has at least one specified attribute"""
        has_who = self.role or self.user_id or self.user_attribute
        has_what = self.column or self.table
        has_when = self.row_condition or self.time_window
        
        if not (has_who or has_what or has_when):
            raise ValueError(
                "PolicyCondition must specify at least one of: "
                "role, user_id, user_attribute (WHO), "
                "column, table (WHAT), or "
                "row_condition, time_window (WHEN)"
            )
    
    def matches(self, user_role: Optional[str] = None,
                user_id: Optional[str] = None,
                user_attributes: Optional[Dict[str, Any]] = None) -> bool:
        """Check if condition matches given user attributes"""
        
        # Check WHO conditions
        if self.role and user_role != self.role:
            return False
        
        if self.user_id and user_id != self.user_id:
            return False
        
        if self.user_attribute and user_attributes:
            for key, value in self.user_attribute.items():
                if user_attributes.get(key) != value:
                    return False
        
        # Note: row_condition and time_window are evaluated during SQL transformation
        # and execution, not at policy matching time
        
        return True


@dataclass
class PolicyAction:
    """
    Action to take when policy applies.
    
    Different actions for different policy types:
    - MASK: mask_value=True, mask_char="*", mask_length=3
    - REDACT: complete column removal from results
    - FILTER: adds WHERE clause to restrict rows
    - AGGREGATE_ONLY: allows only COUNT/SUM/AVG/MIN/MAX queries
    - BLOCK: deny_access=True
    """
    
    # MASK action
    mask: bool = False
    mask_char: str = "*"
    mask_length: int = 3  # Number of replacement characters
    
    # REDACT action
    redact: bool = False
    
    # FILTER action
    where_clause: Optional[str] = None  # WHERE condition to add to SQL
    allow_deleted: bool = False  # Include soft-deleted rows
    
    # AGGREGATE_ONLY action
    aggregate_only: bool = False
    allowed_aggregates: List[str] = field(default_factory=lambda: ["COUNT", "SUM", "AVG", "MIN", "MAX"])
    
    # BLOCK action
    deny_access: bool = False
    deny_reason: str = "Access denied by data policy"
    
    def __post_init__(self):
        """Ensure action is valid"""
        action_count = sum([
            self.mask,
            self.redact,
            self.deny_access,
            self.aggregate_only,
            bool(self.where_clause)
        ])
        
        if action_count == 0:
            raise ValueError("PolicyAction must specify at least one action")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return asdict(self)


@dataclass
class PolicyDefinition:
    """
    Complete policy definition. This is your core product - controlling data access.
    
    Example YAML:
    ```
    policies:
      - name: hide_salary_from_analysts
        description: Analysts cannot see salary column
        type: mask
        condition:
          role: analyst
          column: salary
        action:
          mask: true
          mask_char: "*"
          mask_length: 3
        priority: 10
        enabled: true
    
      - name: hr_only_sensitive_data
        description: Only HR can see sensitive employee data
        type: redact
        condition:
          role: analyst
          table: employees
          column: ssn
        action:
          redact: true
        priority: 5
        enabled: true
    
      - name: regional_sales_filter
        description: Sales people see only their region's data
        type: filter
        condition:
          role: sales
          user_attribute:
            region: us_west
        action:
          where_clause: region = 'us_west'
        priority: 8
        enabled: true
    ```
    """
    
    name: str
    description: str
    type: PolicyType
    condition: PolicyCondition
    action: PolicyAction
    
    # Policy metadata
    priority: int = 10  # 1-100, higher = applied later (override)
    enabled: bool = True
    created_by: str = "system"
    org_id: Optional[str] = None  # For multi-tenant isolation
    
    # Audit
    created_at: str = field(default="")
    updated_at: str = field(default="")
    applies_to_query_types: List[str] = field(default_factory=lambda: ["SELECT"])  # Only SELECT by default
    
    def __post_init__(self):
        """Validate policy definition"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Policy name cannot be empty")
        
        if self.priority < 1 or self.priority > 100:
            raise ValueError("Policy priority must be between 1-100")
        
        if "SELECT" not in self.applies_to_query_types:
            # Ensure SELECT is always included for safety
            self.applies_to_query_types.append("SELECT")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        result = asdict(self)
        result["type"] = self.type.value
        result["condition"] = asdict(self.condition)
        result["action"] = self.action.to_dict()
        return result
    
    def to_yaml(self) -> str:
        """Convert to YAML for file storage"""
        import yaml
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PolicyDefinition":
        """Create PolicyDefinition from dict"""
        # Parse action
        action = PolicyAction(**data.get("action", {}))
        
        # Parse condition
        cond_data = data.get("condition", {})
        time_window = None
        if "time_window" in cond_data:
            tw_data = cond_data.pop("time_window")
            time_window = TimeWindow(**tw_data)
        
        condition = PolicyCondition(time_window=time_window, **cond_data)
        
        # Create policy
        return PolicyDefinition(
            name=data["name"],
            description=data.get("description", ""),
            type=PolicyType(data["type"]),
            condition=condition,
            action=action,
            priority=data.get("priority", 10),
            enabled=data.get("enabled", True),
            created_by=data.get("created_by", "system"),
            org_id=data.get("org_id"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            applies_to_query_types=data.get("applies_to_query_types", ["SELECT"])
        )


@dataclass
class PolicySet:
    """
    Collection of policies for an organization.
    Policies are evaluated in priority order (lower number = earlier).
    """
    
    org_id: str
    policies: List[PolicyDefinition] = field(default_factory=list)
    
    def add_policy(self, policy: PolicyDefinition) -> None:
        """Add policy to set"""
        if policy.org_id and policy.org_id != self.org_id:
            raise ValueError(f"Policy org_id {policy.org_id} does not match set org_id {self.org_id}")
        
        # Ensure unique names within org
        if any(p.name == policy.name for p in self.policies):
            raise ValueError(f"Policy with name '{policy.name}' already exists")
        
        policy.org_id = self.org_id
        self.policies.append(policy)
    
    def remove_policy(self, policy_name: str) -> bool:
        """Remove policy by name, return True if removed"""
        original_count = len(self.policies)
        self.policies = [p for p in self.policies if p.name != policy_name]
        return len(self.policies) < original_count
    
    def get_applicable_policies(
        self,
        user_role: Optional[str] = None,
        user_id: Optional[str] = None,
        user_attributes: Optional[Dict[str, Any]] = None,
        column: Optional[str] = None,
        table: Optional[str] = None
    ) -> List[PolicyDefinition]:
        """
        Get all policies that apply to given user and data context.
        Returns policies sorted by priority (lower first).
        """
        applicable = []
        
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            # Check user conditions
            if not policy.condition.matches(user_role, user_id, user_attributes):
                continue
            
            # Check data conditions
            if policy.condition.column and column:
                if policy.condition.column.lower() != column.lower():
                    continue
            
            if policy.condition.table and table:
                if policy.condition.table.lower() != table.lower():
                    continue
            
            applicable.append(policy)
        
        # Sort by priority (lower number first)
        return sorted(applicable, key=lambda p: p.priority)
    
    def has_blocking_policy(
        self,
        user_role: Optional[str] = None,
        user_id: Optional[str] = None,
        user_attributes: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if any BLOCK policy applies.
        Returns (is_blocked, reason)
        """
        policies = self.get_applicable_policies(user_role, user_id, user_attributes)
        
        for policy in policies:
            if policy.type == PolicyType.BLOCK and policy.action.deny_access:
                return True, policy.action.deny_reason
        
        return False, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "org_id": self.org_id,
            "policies": [p.to_dict() for p in self.policies]
        }
