"""
Multi-tenant Policy Engine - Evaluates SQL queries against organization policies.

Policies can:
- Block queries matching certain patterns
- Require approval for risky operations
- Allow queries that pass all checks
"""
import re
from typing import List, Dict, Any, Tuple
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.db.org_repository import PolicyRepository
from backend.middleware import logger

class OrganizationPolicyEngine:
	"""Evaluates queries against org policies"""
	
	RULE_HANDLERS = {
		"no_full_scan": "_check_no_full_scan",
		"max_joins": "_check_max_joins",
		"max_rows": "_check_max_rows",
		"destructive_check": "_check_destructive",
		"no_cross_join": "_check_no_cross_join",
	}
	
	@staticmethod
	def evaluate_query(org_id: str, sql: str) -> Tuple[List[str], str]:
		"""
		Evaluate a query against all org policies.
		
		Returns:
			(violated_policies, action)
			- violated_policies: List of policy IDs that were violated
			- action: 'block' | 'allow' | 'require_approval'
		"""
		policies = PolicyRepository.get_org_policies(org_id, enabled_only=True)
		violated = []
		max_action = "allow"  # Default: allow if no violations
		
		for policy in policies:
			violated_match = OrganizationPolicyEngine._matches_policy(sql, policy)
			
			if violated_match:
				violated.append(policy["id"])
				
				# Determine action precedence: block > require_approval > allow
				if policy["action"] == "block":
					max_action = "block"
				elif policy["action"] == "require_approval" and max_action != "block":
					max_action = "require_approval"
				
				logger.info({
					"event": "policy_violated",
					"org_id": org_id,
					"policy_id": policy["id"],
					"policy_name": policy["name"],
					"action": policy["action"],
				})
		
		return violated, max_action
	
	@staticmethod
	def _matches_policy(sql: str, policy: Dict) -> bool:
		"""Check if query matches a policy rule"""
		rule_type = policy["rule_type"]
		condition = policy["condition"]
		handler = OrganizationPolicyEngine.RULE_HANDLERS.get(rule_type)
		
		if not handler:
			logger.warning({"event": "unknown_rule_type", "rule_type": rule_type})
			return False
		
		# Call handler method
		handler_method = getattr(OrganizationPolicyEngine, handler)
		return handler_method(sql, condition)
	
	# ==================
	# Rule Handlers
	# ==================
	
	@staticmethod
	def _check_no_full_scan(sql: str, condition: Dict) -> bool:
		"""Detect queries without WHERE clause (full table scans)"""
		sql_upper = sql.upper().strip()
		
		# Check if it's a SELECT without WHERE
		if sql_upper.startswith("SELECT"):
			# Parse structure: SELECT columns FROM table [WHERE ...]
			# Simple heuristic: if no WHERE, it's a full scan
			if " WHERE " not in sql_upper:
				# But allow if it's selecting from a single row or metadata query
				if not any(kw in sql_upper for kw in ["LIMIT 1", "LIMIT 1;", "COUNT(*)"]):
					return True
		
		return False
	
	@staticmethod
	def _check_max_joins(sql: str, condition: Dict) -> bool:
		"""Detect queries with too many JOINs"""
		max_joins = condition.get("max_joins", 3)
		join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
		return join_count > max_joins
	
	@staticmethod
	def _check_max_rows(sql: str, condition: Dict) -> bool:
		"""Detect queries without row limits"""
		max_rows = condition.get("max_rows", 10000)
		
		# Check if query has LIMIT
		if re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE):
			match = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
			if match:
				limit = int(match.group(1))
				return limit > max_rows
		
		# No LIMIT = potential issue
		return True
	
	@staticmethod
	def _check_destructive(sql: str, condition: Dict) -> bool:
		"""Detect destructive operations (DROP, TRUNCATE, DELETE without WHERE)"""
		sql_upper = sql.upper().strip()
		
		destructive_patterns = [
			r"^\s*DROP\s+",
			r"^\s*TRUNCATE\s+",
			r"^\s*DELETE\s+FROM\s+(?!.*\bWHERE\b)",
			r"^\s*ALTER\s+TABLE\s+DROP\s+",
		]
		
		for pattern in destructive_patterns:
			if re.search(pattern, sql, re.IGNORECASE):
				return True
		
		return False
	
	@staticmethod
	def _check_no_cross_join(sql: str, condition: Dict) -> bool:
		"""Detect CROSS JOINs"""
		return bool(re.search(r'\bCROSS\s+JOIN\b', sql, re.IGNORECASE))

# ==================
# Predefined Policies (Starter Templates)
# ==================

STARTER_POLICIES = [
	{
		"name": "No Full Scans",
		"description": "Require WHERE clause on all SELECT queries",
		"rule_type": "no_full_scan",
		"condition": {},
		"action": "block"
	},
	{
		"name": "Max 3 JOINs",
		"description": "Block queries with more than 3 JOINs",
		"rule_type": "max_joins",
		"condition": {"max_joins": 3},
		"action": "require_approval"
	},
	{
		"name": "Max 10k Rows",
		"description": "Require LIMIT on all queries, max 10,000 rows",
		"rule_type": "max_rows",
		"condition": {"max_rows": 10000},
		"action": "require_approval"
	},
	{
		"name": "No Destructive Operations",
		"description": "Block DROP, TRUNCATE, DELETE without WHERE",
		"rule_type": "destructive_check",
		"condition": {},
		"action": "block"
	},
]
