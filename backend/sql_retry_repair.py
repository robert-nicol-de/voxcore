# SQL Retry & Self-Repair Logic for VoxCore
import re

class SQLRetryRepair:
    MAX_RETRIES = 2

    @staticmethod
    def execute_with_retry(executor, sql: str):
        attempts = 0
        last_error = None
        while attempts <= SQLRetryRepair.MAX_RETRIES:
            try:
                return executor(sql)
            except Exception as e:
                last_error = str(e)
                # Example: simple repair for 'column does not exist'
                if 'column' in last_error and 'does not exist' in last_error:
                    # In real system, map semantic alias or try to fix column name
                    sql = SQLRetryRepair.repair_column(sql, last_error)
                attempts += 1
        raise RuntimeError(f"SQL failed after retries: {last_error}")

    @staticmethod
    def repair_column(sql: str, error_msg: str) -> str:
        # Placeholder: real logic would use semantic mapping
        return sql  # No-op for now
