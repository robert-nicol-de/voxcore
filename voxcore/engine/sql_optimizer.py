class SQLAliasManager:
    def generate_aliases(self, base_table, joins):
        alias_map = {}
        # Base table = t (standard)
        alias_map[base_table] = "t"
        # Other tables = a, b, c...
        letters = "abcdefghijklmnopqrstuvwxyz"
        idx = 0
        for j in joins:
            table = j["table"]
            if table not in alias_map:
                alias_map[table] = letters[idx]
                idx += 1
        return alias_map

class SQLAliasApplier:
    def apply(self, plan, alias_map):
        # Update joins
        updated_joins = []
        for j in plan["joins"]:
            join_sql = j["join"]
            for table, alias in alias_map.items():
                join_sql = join_sql.replace(f"{table}.", f"{alias}.")
            updated_joins.append({
                "table": j["table"],
                "alias": alias_map[j["table"]],
                "join": join_sql
            })
        return updated_joins

class SQLOptimizer:
    def optimize(self, sql: str) -> str:
        # Remove double spaces
        sql = " ".join(sql.split())
        # Normalize casing (optional)
        sql = sql.replace("SELECT", "\nSELECT")
        sql = sql.replace("FROM", "\nFROM")
        sql = sql.replace("JOIN", "\nJOIN")
        sql = sql.replace("GROUP BY", "\nGROUP BY")
        sql = sql.replace("ORDER BY", "\nORDER BY")
        return sql
