"""
Comprehensive tests for STEP 8 — Data Policy Engine

Tests cover:
- Policy definitions and validation
- Pre-execution SQL transformation
- Post-execution result masking
- Policy engine evaluation
- Edge cases and security
"""

import pytest
from datetime import time
from typing import Dict, List, Any

from backend.services.policy_definition import (
    PolicyDefinition, PolicyCondition, PolicyAction, PolicySet,
    PolicyType, TimeWindow
)
from backend.services.pre_execution_policy_applier import PreExecutionPolicyApplier
from backend.services.post_execution_policy_applier import PostExecutionPolicyApplier, ResultMetadata
from backend.services.policy_engine import PolicyEngine


class TestPolicyDefinition:
    """Test policy definition and validation"""
    
    def test_create_mask_policy(self):
        """Test creating a MASK policy"""
        condition = PolicyCondition(role="analyst", column="salary")
        action = PolicyAction(mask=True, mask_char="*", mask_length=3)
        policy = PolicyDefinition(
            name="hide_salary",
            description="Hide salary from analysts",
            type=PolicyType.MASK,
            condition=condition,
            action=action
        )
        
        assert policy.name == "hide_salary"
        assert policy.type == PolicyType.MASK
        assert policy.action.mask is True
    
    def test_create_redact_policy(self):
        """Test creating a REDACT policy"""
        condition = PolicyCondition(role="analyst", column="ssn")
        action = PolicyAction(redact=True)
        policy = PolicyDefinition(
            name="hide_ssn",
            description="Hide SSN",
            type=PolicyType.REDACT,
            condition=condition,
            action=action
        )
        
        assert policy.type == PolicyType.REDACT
        assert policy.action.redact is True
    
    def test_create_filter_policy(self):
        """Test creating a FILTER policy"""
        condition = PolicyCondition(role="sales", user_attribute={"region": "us_west"})
        action = PolicyAction(where_clause="region = 'us_west'")
        policy = PolicyDefinition(
            name="sales_regional_filter",
            description="Sales see only their region",
            type=PolicyType.FILTER,
            condition=condition,
            action=action
        )
        
        assert policy.type == PolicyType.FILTER
        assert policy.action.where_clause == "region = 'us_west'"
    
    def test_create_aggregate_only_policy(self):
        """Test creating AGGREGATE_ONLY policy"""
        condition = PolicyCondition(role="viewer")
        action = PolicyAction(aggregate_only=True)
        policy = PolicyDefinition(
            name="viewer_aggregate_only",
            description="Viewers only see aggregates",
            type=PolicyType.AGGREGATE_ONLY,
            condition=condition,
            action=action
        )
        
        assert policy.type == PolicyType.AGGREGATE_ONLY
    
    def test_create_block_policy(self):
        """Test creating a BLOCK policy"""
        condition = PolicyCondition(user_id="blocked_user_123")
        action = PolicyAction(deny_access=True, deny_reason="User suspended")
        policy = PolicyDefinition(
            name="block_suspended_user",
            description="Block suspended user",
            type=PolicyType.BLOCK,
            condition=condition,
            action=action
        )
        
        assert policy.type == PolicyType.BLOCK
        assert policy.action.deny_access is True
    
    def test_policy_condition_matching(self):
        """Test policy condition matching"""
        condition = PolicyCondition(role="analyst", column="salary")
        
        # Should match
        assert condition.matches(user_role="analyst")
        
        # Should not match
        assert not condition.matches(user_role="admin")
        assert not condition.matches(user_role=None)
    
    def test_policy_condition_requires_at_least_one_attribute(self):
        """Test that policy condition requires at least one attribute"""
        with pytest.raises(ValueError):
            PolicyCondition()  # No attributes
    
    def test_policy_action_requires_action_type(self):
        """Test that policy action requires at least one action"""
        with pytest.raises(ValueError):
            PolicyAction()  # No action specified
    
    def test_policy_priority_validation(self):
        """Test priority bounds checking"""
        condition = PolicyCondition(role="analyst")
        action = PolicyAction(mask=True)
        
        # Valid range: 1-100
        policy = PolicyDefinition(
            name="test",
            description="test",
            type=PolicyType.MASK,
            condition=condition,
            action=action,
            priority=50
        )
        assert policy.priority == 50
        
        # Invalid: below 1
        with pytest.raises(ValueError):
            PolicyDefinition(
                name="test",
                description="test",
                type=PolicyType.MASK,
                condition=condition,
                action=action,
                priority=0
            )
    
    def test_policy_set_operations(self):
        """Test policy set add/remove"""
        policy_set = PolicySet(org_id="acme")
        
        condition = PolicyCondition(role="analyst", column="salary")
        action = PolicyAction(mask=True)
        policy = PolicyDefinition(
            name="hide_salary",
            description="Hide salary",
            type=PolicyType.MASK,
            condition=condition,
            action=action
        )
        
        policy_set.add_policy(policy)
        assert len(policy_set.policies) == 1
        
        removed = policy_set.remove_policy("hide_salary")
        assert removed is True
        assert len(policy_set.policies) == 0


class TestPreExecutionPolicyApplier:
    """Test SQL transformation before execution"""
    
    def test_add_where_clause_no_existing_where(self):
        """Test adding WHERE clause to query without WHERE"""
        applier = PreExecutionPolicyApplier()
        sql = "SELECT * FROM customers"
        
        result = applier._add_where_clauses(sql, ["org_id = 'acme'"])
        
        assert "WHERE" in result
        assert "org_id = 'acme'" in result
    
    def test_add_where_clause_with_existing_where(self):
        """Test adding WHERE clause to query with existing WHERE"""
        applier = PreExecutionPolicyApplier()
        sql = "SELECT * FROM customers WHERE status = 'active'"
        
        result = applier._add_where_clauses(sql, ["org_id = 'acme'"])
        
        assert "WHERE" in result
        assert "status = 'active'" in result
        assert "org_id = 'acme'" in result
        assert "AND" in result
    
    def test_apply_policies_with_filter(self):
        """Test applying FILTER policy"""
        applier = PreExecutionPolicyApplier()
        sql = "SELECT * FROM orders"
        
        condition = PolicyCondition(role="sales")
        action = PolicyAction(where_clause="region = 'us_west'")
        policy = PolicyDefinition(
            name="sales_filter",
            description="Regional filter",
            type=PolicyType.FILTER,
            condition=condition,
            action=action
        )
        
        result, effects = applier.apply_policies(sql, [policy])
        
        assert "WHERE" in result
        assert "region = 'us_west'" in result
        assert "filters_applied:1" in effects
    
    def test_apply_policies_with_block(self):
        """Test that BLOCK policy raises exception"""
        applier = PreExecutionPolicyApplier()
        sql = "SELECT * FROM salary_data"
        
        condition = PolicyCondition(role="analyst")
        action = PolicyAction(deny_access=True, deny_reason="Access denied: sensitive data")
        policy = PolicyDefinition(
            name="block_sensitive",
            description="Block sensitive",
            type=PolicyType.BLOCK,
            condition=condition,
            action=action
        )
        
        with pytest.raises(RuntimeError):
            applier.apply_policies(sql, [policy])
    
    def test_apply_aggregate_only_policy(self):
        """Test AGGREGATE_ONLY policy forces aggregation"""
        applier = PreExecutionPolicyApplier()
        sql = "SELECT customer_id, total FROM orders"
        
        condition = PolicyCondition(role="viewer")
        action = PolicyAction(aggregate_only=True)
        policy = PolicyDefinition(
            name="agg_only",
            description="Aggregate only",
            type=PolicyType.AGGREGATE_ONLY,
            condition=condition,
            action=action
        )
        
        result, effects = applier.apply_policies(sql, [policy])
        
        # Should transform to use COUNT(*)
        assert "COUNT(*)" in result.upper()
        assert "aggregate_only_enforced" in effects


class TestPostExecutionPolicyApplier:
    """Test result masking after execution"""
    
    def test_redact_columns(self):
        """Test column redaction (removal)"""
        applier = PostExecutionPolicyApplier()
        
        results = [
            {"id": 1, "name": "Alice", "ssn": "123-45-6789", "salary": 100000},
            {"id": 2, "name": "Bob", "ssn": "987-65-4321", "salary": 120000}
        ]
        
        redacted = applier._redact_columns(results, {"ssn", "salary"})
        
        # Check that ssn and salary are gone
        assert all("ssn" not in row for row in redacted)
        assert all("salary" not in row for row in redacted)
        
        # Check that id and name remain
        assert redacted[0]["id"] == 1
        assert redacted[0]["name"] == "Alice"
    
    def test_mask_columns(self):
        """Test column masking (value replacement)"""
        applier = PostExecutionPolicyApplier()
        
        results = [
            {"id": 1, "name": "Alice", "salary": 100000},
            {"id": 2, "name": "Bob", "salary": 120000}
        ]
        
        masked = applier._mask_columns(
            results,
            {"salary": ("*", 3)}
        )
        
        # Check that salary is masked
        assert masked[0]["salary"] == "***"
        assert masked[1]["salary"] == "***"
        
        # Check that id and name remain
        assert masked[0]["id"] == 1
        assert masked[0]["name"] == "Alice"
    
    def test_apply_policies_with_mask_and_redact(self):
        """Test applying both MASK and REDACT policies"""
        applier = PostExecutionPolicyApplier()
        
        results = [
            {"id": 1, "name": "Alice", "ssn": "123-45-6789", "salary": 100000}
        ]
        
        # Create policies
        mask_policy = PolicyDefinition(
            name="mask_salary",
            description="Mask salary",
            type=PolicyType.MASK,
            condition=PolicyCondition(column="salary"),
            action=PolicyAction(mask=True)
        )
        
        redact_policy = PolicyDefinition(
            name="redact_ssn",
            description="Redact SSN",
            type=PolicyType.REDACT,
            condition=PolicyCondition(column="ssn"),
            action=PolicyAction(redact=True)
        )
        
        result, effects = applier.apply_policies(results, [mask_policy, redact_policy])
        
        # Check salary is masked
        assert result[0]["salary"] == "***"
        
        # Check ssn is removed
        assert "ssn" not in result[0]
        
        # Check id and name remain
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
    
    def test_safe_columns(self):
        """Test identifying safe (unmasked/unredacted) columns"""
        applier = PostExecutionPolicyApplier()
        
        results = [
            {"id": 1, "name": "Alice", "salary": 100000, "ssn": "123-45-6789"}
        ]
        
        safe = applier.get_safe_columns(results, {"ssn"}, {"salary"})
        
        assert "id" in safe
        assert "name" in safe
        assert "salary" not in safe
        assert "ssn" not in safe
    
    def test_result_metadata(self):
        """Test result metadata tracking"""
        metadata = ResultMetadata()
        
        metadata.add_mask("salary", "*")
        metadata.add_redact("ssn")
        metadata.add_policy("hide_salary_from_analyst")
        metadata.add_warning("Some data has been masked")
        
        result = metadata.to_dict()
        
        assert "salary" in result["masked_columns"]
        assert "ssn" in result["redacted_columns"]
        assert "hide_salary_from_analyst" in result["policies_applied"]
        assert len(result["warnings"]) > 0


class TestPolicyEngine:
    """Test core policy engine"""
    
    def test_extract_columns_from_sql(self):
        """Test column extraction from SQL"""
        engine = PolicyEngine()
        
        sql = "SELECT id, name, salary FROM employees"
        columns = engine.extract_columns_from_sql(sql)
        
        assert "id" in columns
        assert "name" in columns
        assert "salary" in columns
    
    def test_extract_tables_from_sql(self):
        """Test table extraction from SQL"""
        engine = PolicyEngine()
        
        sql = "SELECT * FROM customers JOIN orders ON customers.id = orders.customer_id"
        tables = engine.extract_tables_from_sql(sql)
        
        assert "customers" in tables
        assert "orders" in tables
    
    def test_is_aggregate_query(self):
        """Test aggregate query detection"""
        engine = PolicyEngine()
        
        # Aggregate
        assert engine.is_aggregate_query("SELECT COUNT(*) FROM orders") is True
        assert engine.is_aggregate_query("SELECT SUM(salary) FROM employees") is True
        
        # Non-aggregate
        assert engine.is_aggregate_query("SELECT * FROM customers") is False
    
    def test_get_affected_data(self):
        """Test affected data analysis"""
        engine = PolicyEngine()
        
        sql = "SELECT id, name, salary FROM employees"
        affected = engine.get_affected_data(sql)
        
        assert "id" in affected["columns"]
        assert "name" in affected["columns"]
        assert "salary" in affected["columns"]
        assert "employees" in affected["tables"]
        assert affected["is_aggregate"] is False
    
    def test_add_and_retrieve_policies(self):
        """Test adding and retrieving policies"""
        engine = PolicyEngine()
        
        condition = PolicyCondition(role="analyst", column="salary")
        action = PolicyAction(mask=True)
        policy = PolicyDefinition(
            name="hide_salary",
            description="Hide salary",
            type=PolicyType.MASK,
            condition=condition,
            action=action
        )
        
        engine.add_policy("acme", policy)
        
        policies = engine.get_policies("acme")
        assert len(policies) == 1
        assert policies[0].name == "hide_salary"
    
    def test_get_applicable_policies(self):
        """Test getting applicable policies"""
        engine = PolicyEngine()
        
        # Add a policy for analysts
        condition = PolicyCondition(role="analyst", column="salary")
        action = PolicyAction(mask=True)
        policy = PolicyDefinition(
            name="hide_salary_from_analyst",
            description="Hide",
            type=PolicyType.MASK,
            condition=condition,
            action=action
        )
        
        engine.add_policy("acme", policy)
        
        # Get applicable policies for analyst
        applicable = engine.get_applicable_policies(
            org_id="acme",
            user_role="analyst",
            column="salary"
        )
        
        assert len(applicable) == 1
        
        # Get applicable policies for admin (shouldn't match)
        applicable_admin = engine.get_applicable_policies(
            org_id="acme",
            user_role="admin",
            column="salary"
        )
        
        assert len(applicable_admin) == 0


class TestE2EPolicyEngine:
    """End-to-end integration tests"""
    
    def test_full_pipeline_mask_salary(self):
        """Test full pipeline: query execution with salary masking"""
        # Setup
        engine = PolicyEngine()
        pre_applier = PreExecutionPolicyApplier()
        post_applier = PostExecutionPolicyApplier()
        
        # Define policy
        condition = PolicyCondition(role="analyst")
        action = PolicyAction(mask=True, mask_char="*", mask_length=3)
        policy = PolicyDefinition(
            name="mask_salary",
            description="Mask salary for analysts",
            type=PolicyType.MASK,
            condition=PolicyCondition(role="analyst", column="salary"),
            action=action
        )
        
        engine.add_policy("acme", policy)
        
        # Simulate query execution
        sql = "SELECT id, name, salary FROM employees"
        mock_results = [
            {"id": 1, "name": "Alice", "salary": 100000},
            {"id": 2, "name": "Bob", "salary": 120000}
        ]
        
        # Get applicable policies
        policies = engine.get_applicable_policies(
            org_id="acme",
            user_role="analyst",
            column="salary"
        )
        
        # Apply post-execution masking
        masked_results, effects = post_applier.apply_policies(mock_results, policies)
        
        # Verify results
        assert masked_results[0]["salary"] == "***"
        assert masked_results[0]["name"] == "Alice"  # Not masked
        assert "masked_columns:1" in effects
    
    def test_full_pipeline_filter_region(self):
        """Test full pipeline: regional filtering"""
        engine = PolicyEngine()
        pre_applier = PreExecutionPolicyApplier()
        
        # Define policy
        policy = PolicyDefinition(
            name="region_filter",
            description="Sales see only their region",
            type=PolicyType.FILTER,
            condition=PolicyCondition(
                role="sales",
                user_attribute={"region": "us_west"}
            ),
            action=PolicyAction(where_clause="region = 'us_west'")
        )
        
        engine.add_policy("acme", policy)
        
        # Get applicable policies
        policies = engine.get_applicable_policies(
            org_id="acme",
            user_role="sales",
            user_attributes={"region": "us_west"}
        )
        
        # Apply pre-execution filtering
        sql = "SELECT * FROM accounts WHERE active = true"
        filtered_sql, effects = pre_applier.apply_policies(sql, policies)
        
        # Verify filtering was applied
        assert "region = 'us_west'" in filtered_sql
        assert "filters_applied:1" in effects
    
    def test_multi_policy_interaction(self):
        """Test interaction of multiple policies"""
        engine = PolicyEngine()
        
        # Policy 1: Mask salary for analysts
        policy1 = PolicyDefinition(
            name="mask_salary",
            description="Mask salary",
            type=PolicyType.MASK,
            condition=PolicyCondition(role="analyst", column="salary"),
            action=PolicyAction(mask=True)
        )
        
        # Policy 2: Redact SSN for analysts
        policy2 = PolicyDefinition(
            name="redact_ssn",
            description="Redact SSN",
            type=PolicyType.REDACT,
            condition=PolicyCondition(role="analyst", column="ssn"),
            action=PolicyAction(redact=True)
        )
        
        engine.add_policy("acme", policy1)
        engine.add_policy("acme", policy2)
        
        # Get all policies for analyst
        applicable = engine.get_applicable_policies(
            org_id="acme",
            user_role="analyst"
        )
        
        assert len(applicable) == 2


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
