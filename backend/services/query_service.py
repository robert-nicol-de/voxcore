
# --- Masking utilities ---
def mask_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return "***"
    user, domain = email.split("@", 1)
    if len(user) <= 2:
        masked_user = user[0] + "*" * (len(user)-1)
    else:
        masked_user = user[0] + "*" * (len(user)-2) + user[-1]
    return f"{masked_user}@{domain}"

def mask_ssn(ssn: str) -> str:
    if not isinstance(ssn, str) or len(ssn) < 4:
        return "***"
    return "***-**-" + ssn[-4:]

def mask_credit_card(card: str) -> str:
    if not isinstance(card, str) or len(card) < 4:
        return "****"
    return "**** **** **** " + card[-4:]

def mask_salary(salary) -> str:
    return "*****"

def mask_password(pw: str) -> str:
    return "********"

def mask_generic(value: str) -> str:
    return "***"

MASKING_RULES = {
    "email": mask_email,
    "ssn": mask_ssn,
    "social_security_number": mask_ssn,
    "credit_card": mask_credit_card,
    "credit_card_number": mask_credit_card,
    "salary": mask_salary,
    "password": mask_password,
    "private_key": mask_generic,
    "api_key": mask_generic,
    "secret_key": mask_generic,
    "access_token": mask_generic,
    "refresh_token": mask_generic,
    "bank_account": mask_generic,
    "routing_number": mask_generic,
}

def mask_sensitive_columns_in_row(row: dict, columns_to_mask: set) -> dict:
    for col in columns_to_mask:
        if col in row:
            func = MASKING_RULES.get(col.lower(), mask_generic)
            row[col] = func(row[col])
    return row
# --- BEGIN: Import Path Debug and Lockdown ---
import os
print("RUNNING QUERY SERVICE FROM:", os.path.abspath(__file__))
if __name__ != "backend.services.query_service":
    raise RuntimeError("Wrong query_service loaded")
# --- END: Import Path Debug and Lockdown ---



import os
import sys
import logging
from voxcore.engine.main_query_engine import process_user_question

# Enforce ASCII-only logs and safe logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Canonical file info (ASCII only)
logger.info(f"USING CANONICAL: {os.path.abspath(__file__)}")
logger.debug(f"sys.path: {sys.path}")

class QueryService:
    def __init__(self, db):
        self.db = db

    def execute(self, query_request, user=None):
        """
        Orchestrates the analytics pipeline using VoxCore's main engine.
        """
        if not hasattr(query_request, "question") or not query_request.question or not query_request.question.strip():
            logger.error("Validation failed: question is empty", extra={"question": getattr(query_request, 'question', None)})
            raise ValueError("Query cannot be empty.")

        logger.info("Executing query", extra={"question": query_request.question, "user": user})

        # --- Policy enforcement: get columns to mask ---
        from backend.services.policy_engine import apply_policies
        company_id = getattr(user, "company_id", "default") if user else "default"
        actor_role = getattr(user, "role", None) if user else None
        # For analysis, try to extract columns/tables from the question (could be improved)
        analysis = {"columns": [], "tables": []}
        # Optionally, use a SQL analysis step here
        policy_result = apply_policies(company_id, query_request.question, analysis, actor_role)
        columns_to_mask = set(policy_result.get("columns_to_mask") or [])

        # Use VoxCore's main engine for all analytics
        result = process_user_question(
            question=query_request.question,
            db_connection=self.db
        )


        # Mask denied columns in result (if tabular data)
        if isinstance(result, dict) and "data" in result and isinstance(result["data"], list):
            for row in result["data"]:
                mask_sensitive_columns_in_row(row, columns_to_mask)

        logger.info("VoxCore result", extra={"result": result})
        return result
