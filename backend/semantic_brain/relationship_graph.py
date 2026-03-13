from __future__ import annotations

from collections import deque


class RelationshipGraph:
    def __init__(self, relationships: set[tuple[str, str]] | None = None) -> None:
        self.relationships: set[tuple[str, str]] = relationships or set()

    @classmethod
    def from_schema(cls, schema_rows: list[dict]) -> "RelationshipGraph":
        primary_keys: dict[str, str] = {}
        foreign_key_candidates: list[tuple[str, str, str]] = []

        for table in schema_rows:
            table_name = str(table.get("table_name") or "")
            if not table_name:
                continue
            for col in table.get("columns", []):
                column_name = str(col.get("column_name") or "")
                if not column_name:
                    continue
                fq_col = f"{table_name}.{column_name}"
                if col.get("primary_key"):
                    primary_keys[fq_col] = table_name
                if column_name.endswith("_id"):
                    foreign_key_candidates.append((table_name, column_name, fq_col))

        relationships: set[tuple[str, str]] = set()
        for table_name, column_name, fq_col in foreign_key_candidates:
            base = column_name[:-3]
            target = None
            for pk_col, pk_table in primary_keys.items():
                if pk_table == table_name:
                    continue
                pk_name = pk_col.split(".", 1)[1]
                if pk_name == column_name or pk_name == f"{base}_id" or pk_name == "id":
                    target = pk_col
                    break
            if target:
                relationships.add((fq_col, target))

        return cls(relationships)

    def get_join_path(self, table_a: str, table_b: str) -> list[tuple[str, str]]:
        if table_a == table_b:
            return []

        graph: dict[str, set[str]] = {}
        edge_map: dict[tuple[str, str], tuple[str, str]] = {}

        for source, target in self.relationships:
            src_table = source.split(".", 1)[0]
            tgt_table = target.split(".", 1)[0]
            graph.setdefault(src_table, set()).add(tgt_table)
            graph.setdefault(tgt_table, set()).add(src_table)
            edge_map[(src_table, tgt_table)] = (source, target)
            edge_map[(tgt_table, src_table)] = (target, source)

        queue = deque([(table_a, [])])
        seen = {table_a}

        while queue:
            current, path = queue.popleft()
            for neighbor in graph.get(current, set()):
                if neighbor in seen:
                    continue
                edge = edge_map.get((current, neighbor))
                next_path = path + ([edge] if edge else [])
                if neighbor == table_b:
                    return next_path
                seen.add(neighbor)
                queue.append((neighbor, next_path))

        return []

    def to_prompt_lines(self, max_items: int = 20) -> list[str]:
        lines: list[str] = []
        for source, target in list(self.relationships)[:max_items]:
            lines.append(f"- {source} -> {target}")
        return lines
