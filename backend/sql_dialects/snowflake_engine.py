# Example: Snowflake SQL dialect engine for VoxCore
from .base_engine import BaseSQLEngine
from backend.neutral_query import NeutralQuery

class SnowflakeEngine(BaseSQLEngine):
    dialect_name = "snowflake"

    def to_sql(self, nq: NeutralQuery) -> str:
        select_cols = []
        if nq.aggregations:
            for agg in nq.aggregations:
                select_cols.append(f"{agg['agg'].upper()}({agg['column']}) AS {agg['column']}")
        else:
            select_cols.append(nq.metric)
        if nq.group_by:
            select_cols.extend(nq.group_by)
        select_clause = ", ".join(select_cols)
        sql = f"SELECT {select_clause} FROM {nq.table}"
        if nq.filters:
            where = " AND ".join([f"{f['column']} {f['op']} '{f['value']}'" for f in nq.filters])
            sql += f" WHERE {where}"
        if nq.group_by:
            sql += f" GROUP BY {', '.join(nq.group_by)}"
        if nq.sort:
            sql += f" ORDER BY {nq.sort}"
        if nq.limit:
            sql += f" LIMIT {nq.limit}"
        return sql
