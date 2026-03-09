"""
Policy Generator for Data Sensitivity Findings

Automatically generates security policies based on sensitivity scanner findings.

Author: VoxCore
Date: March 2026
"""

from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from sensitivity_scanner import SensitiveColumn


@dataclass
class GeneratedPolicy:
    """Represents an auto-generated security policy"""
    policy_name: str
    description: str
    mask_columns: List[str]  # PII columns that should be masked
    deny_tables: List[str]  # SECRET columns' tables that should be blocked
    deny_columns: List[str]  # Individual columns that should be blocked
    max_rows: int  # Maximum rows that can be returned
    allow_ai_access: bool  # Whether AI can directly access
    require_approval: bool  # Whether modifications require approval
    audit_all: bool  # Whether to audit all access
    recommendations: List[str]

    def to_dict(self):
        return asdict(self)

    def to_ini_format(self) -> str:
        """Convert policy to INI format for storage"""
        lines = [f"[policy_{self.policy_name}]"]
        lines.append(f"description = {self.description}")
        if self.mask_columns:
            lines.append(f"mask_columns = {','.join(self.mask_columns)}")
        if self.deny_tables:
            lines.append(f"deny_tables = {','.join(self.deny_tables)}")
        if self.deny_columns:
            lines.append(f"deny_columns = {','.join(self.deny_columns)}")
        lines.append(f"max_rows = {self.max_rows}")
        lines.append(f"allow_ai_access = {str(self.allow_ai_access).lower()}")
        lines.append(f"require_approval = {str(self.require_approval).lower()}")
        lines.append(f"audit_all = {str(self.audit_all).lower()}")
        return "\n".join(lines)


class PolicyGenerator:
    """
    Generates security policies from sensitivity scanner findings.
    
    Policy Strategies:
    - SECRET columns → Block table, require approval
    - PII columns → Mask, audit all access
    - FINANCIAL columns → Restrict, AI access requires approval
    - HEALTH columns → Restrict, require approval for all access
    """

    # Risk thresholds
    HIGH_RISK_THRESHOLD = 0.85  # Confidence threshold for high-risk findings
    MEDIUM_RISK_THRESHOLD = 0.70

    def generate_policy(self, scan_results: Dict, connector_name: str) -> GeneratedPolicy:
        """
        Generate a comprehensive security policy from scan results.
        
        Args:
            scan_results: Results from SensitivityScanner.scan_schema()
            connector_name: Name of the database connector
        
        Returns:
            GeneratedPolicy object
        """
        policy_name = f"{connector_name}_auto"
        secret_columns = scan_results["by_type"].get("secret", [])
        pii_columns = scan_results["by_type"].get("pii", [])
        financial_columns = scan_results["by_type"].get("financial", [])
        health_columns = scan_results["by_type"].get("health", [])

        # Extract column paths
        secret_paths = [
            f"{c['table_name']}.{c['column_name']}" for c in secret_columns
            if c["confidence"] >= self.HIGH_RISK_THRESHOLD
        ]
        pii_paths = [
            f"{c['table_name']}.{c['column_name']}" for c in pii_columns
            if c["confidence"] >= self.MEDIUM_RISK_THRESHOLD
        ]
        financial_paths = [
            f"{c['table_name']}.{c['column_name']}" for c in financial_columns
            if c["confidence"] >= self.MEDIUM_RISK_THRESHOLD
        ]
        health_paths = [
            f"{c['table_name']}.{c['column_name']}" for c in health_columns
            if c["confidence"] >= self.MEDIUM_RISK_THRESHOLD
        ]

        # Extract tables with secret columns
        secret_tables = set(c["table_name"] for c in secret_columns)

        # Build policy
        mask_columns = pii_paths + health_paths
        deny_columns = secret_paths
        risk_summary = scan_results.get("risk_summary", {})

        # Determine restrictions based on risk
        allow_ai_access = risk_summary.get("critical", 0) == 0
        require_approval = risk_summary.get("critical", 0) > 0 or risk_summary.get("high", 0) > 3
        audit_all = True  # Always audit

        # Generate recommendations
        recommendations = self._generate_recommendations(
            scan_results, secret_tables, pii_paths, financial_paths, health_paths
        )

        description = self._generate_description(scan_results)

        return GeneratedPolicy(
            policy_name=policy_name,
            description=description,
            mask_columns=mask_columns,
            deny_tables=list(secret_tables),
            deny_columns=deny_columns,
            max_rows=1000,
            allow_ai_access=allow_ai_access,
            require_approval=require_approval,
            audit_all=audit_all,
            recommendations=recommendations,
        )

    def _generate_description(self, scan_results: Dict) -> str:
        """Generate a human-readable policy description"""
        risk = scan_results.get("risk_summary", {})
        critical = risk.get("critical", 0)
        high = risk.get("high", 0)
        medium = risk.get("medium", 0)

        if critical > 0:
            return f"Strict policy: {critical} critical secrets detected"
        elif high > 0:
            return f"Protected policy: {high} sensitive data columns detected"
        elif medium > 0:
            return f"Standard policy: {medium} health/sensitive columns detected"
        else:
            return "Standard protection policy"

    def _generate_recommendations(
        self,
        scan_results: Dict,
        secret_tables: Set[str],
        pii_paths: List[str],
        financial_paths: List[str],
        health_paths: List[str],
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if secret_tables:
            recommendations.append(
                f"🔴 Block direct access to: {', '.join(secret_tables)}"
            )
            recommendations.append("Require approval for all queries on sensitive tables")

        if pii_paths:
            recommendations.append(
                f"👤 Mask {len(pii_paths)} PII column(s): {', '.join(pii_paths[:3])}"
                + (f" + {len(pii_paths) - 3} more" if len(pii_paths) > 3 else "")
            )

        if financial_paths:
            recommendations.append(
                f"💳 Restrict {len(financial_paths)} financial column(s)"
            )

        if health_paths:
            recommendations.append(
                f"🏥 Apply HIPAA-level protection to {len(health_paths)} health column(s)"
            )

        recommendations.extend([
            "✅ Enable audit logging for all queries",
            "✅ Implement row-level security by role",
            "✅ Add data access approval workflows",
            "✅ Schedule quarterly policy reviews",
        ])

        return recommendations

    def generate_mask_map(self, scan_results: Dict) -> Dict[str, str]:
        """
        Generate column masking specifications.
        
        Returns mapping of column to masking type:
        - email → partial (show ***.***@domain.com)
        - phone → partial (show last 4 digits)
        - ssn → partial (show last 4 digits)
        - card → full (mask all digits)
        - password → full (never show)
        """
        mask_map = {}

        pii_columns = scan_results["by_type"].get("pii", [])
        for col in pii_columns:
            col_lower = col["column_name"].lower()
            if "email" in col_lower:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "email_partial"
            elif "phone" in col_lower or "telephone" in col_lower:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "phone_last4"
            elif "ssn" in col_lower or "social" in col_lower:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "ssn_last4"
            else:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "full_mask"

        financial_columns = scan_results["by_type"].get("financial", [])
        for col in financial_columns:
            col_lower = col["column_name"].lower()
            if "card" in col_lower:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "card_last4"
            elif "cvv" in col_lower or "cvc" in col_lower:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "full_mask"
            else:
                mask_map[f"{col['table_name']}.{col['column_name']}"] = "full_mask"

        secret_columns = scan_results["by_type"].get("secret", [])
        for col in secret_columns:
            mask_map[f"{col['table_name']}.{col['column_name']}"] = "blocked"

        health_columns = scan_results["by_type"].get("health", [])
        for col in health_columns:
            mask_map[f"{col['table_name']}.{col['column_name']}"] = "full_mask"

        return mask_map

    def apply_policy_to_connector_config(
        self, policy: GeneratedPolicy, config_path: str
    ) -> bool:
        """
        Apply generated policy to connector configuration file.
        
        Args:
            policy: GeneratedPolicy object
            config_path: Path to connector config file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(config_path, "a") as f:
                f.write("\n\n")
                f.write(policy.to_ini_format())
            return True
        except Exception as e:
            print(f"Error applying policy: {e}")
            return False
