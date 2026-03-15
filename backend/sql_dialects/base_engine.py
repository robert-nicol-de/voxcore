# Base class for SQL dialect engines in VoxCore
from backend.neutral_query import NeutralQuery

class BaseSQLEngine:
    dialect_name = "base"

    def to_sql(self, nq: NeutralQuery) -> str:
        """Convert a NeutralQuery to dialect-specific SQL. To be implemented by subclasses."""
        raise NotImplementedError

    # Optionally, add methods for function mapping, identifier quoting, etc.
