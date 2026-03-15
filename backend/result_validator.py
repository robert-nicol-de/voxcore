# SQL Result Validation Layer for VoxCore

class ResultValidator:
    @staticmethod
    def validate(results):
        # Example checks: nulls, impossible values, empty results, outliers
        if not results or len(results) == 0:
            return False, "Empty result set"
        # Example: check for impossible negative revenue
        for row in results:
            for value in row.values():
                if isinstance(value, (int, float)) and value < -1e8:
                    return False, f"Suspicious value detected: {value}"
        return True, "Results valid"
