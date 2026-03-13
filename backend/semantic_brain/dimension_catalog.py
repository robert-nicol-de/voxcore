from __future__ import annotations

from typing import Any


class DimensionCatalog:
    def __init__(self, dimensions: dict[str, dict[str, str]] | None = None) -> None:
        self.dimensions: dict[str, dict[str, str]] = dimensions or {
            "district": {"table": "sales", "column": "district"},
            "product_category": {"table": "sales", "column": "product_category"},
        }

    @classmethod
    def from_semantic_models_and_schema(
        cls,
        semantic_models: list[dict[str, Any]],
        schema_rows: list[dict[str, Any]],
    ) -> "DimensionCatalog":
        catalog = cls()

        for model in semantic_models:
            definition = model.get("definition") if isinstance(model, dict) else None
            if not isinstance(definition, dict):
                continue
            model_dims = definition.get("dimensions")
            if not isinstance(model_dims, dict):
                continue
            for dim_name, payload in model_dims.items():
                item = payload if isinstance(payload, dict) else {}
                catalog.dimensions[str(dim_name).lower()] = {
                    "table": str(item.get("table") or ""),
                    "column": str(item.get("column") or dim_name),
                }

        for table in schema_rows:
            table_name = str(table.get("table_name") or "")
            if not table_name:
                continue
            for col in table.get("columns", []):
                col_name = str(col.get("column_name") or "")
                data_type = str(col.get("data_type") or "").lower()
                if not col_name:
                    continue
                if any(token in data_type for token in ["int", "decimal", "float", "numeric", "money"]):
                    continue
                key = col_name.lower()
                if key not in catalog.dimensions:
                    catalog.dimensions[key] = {"table": table_name, "column": col_name}
        return catalog

    def get_dimension(self, name: str) -> dict[str, str] | None:
        return self.dimensions.get((name or "").strip().lower())

    def to_prompt_lines(self, max_items: int = 20) -> list[str]:
        lines: list[str] = []
        for key in list(self.dimensions.keys())[:max_items]:
            payload = self.dimensions[key]
            lines.append(f"- {key} ({payload.get('table', '')}.{payload.get('column', '')})")
        return lines
