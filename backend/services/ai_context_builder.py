from __future__ import annotations

from typing import Any

import backend.db.org_store as store


def _format_schema_lines(workspace_id: int, max_tables: int = 30, max_columns: int = 10) -> list[str]:
    snapshot = store.list_workspace_schema_snapshot(workspace_id, max_tables=max_tables, max_columns_per_table=max_columns)
    lines: list[str] = []
    for table in snapshot:
        schema_name = table.get('schema_name') or 'public'
        table_name = table.get('table_name') or ''
        if not table_name:
            continue

        col_parts: list[str] = []
        for col in table.get('columns', [])[:max_columns]:
            col_name = col.get('column_name') or ''
            if not col_name:
                continue
            type_name = col.get('data_type') or 'unknown'
            marker: list[str] = []
            if col.get('primary_key'):
                marker.append('pk')
            if col.get('sensitive'):
                marker.append(f"sensitive:{col.get('sensitive')}")
            marker_text = f" [{'|'.join(marker)}]" if marker else ''
            col_parts.append(f"{col_name}:{type_name}{marker_text}")

        datasource_name = table.get('datasource_name') or 'datasource'
        platform = table.get('platform') or 'unknown'
        lines.append(
            f"- {datasource_name}/{platform} {schema_name}.{table_name}({', '.join(col_parts)})"
        )
    return lines


def _format_semantic_lines(workspace_id: int, max_models: int = 5, max_entities: int = 8) -> list[str]:
    models = store.list_semantic_models(workspace_id)
    lines: list[str] = []

    for model in models[:max_models]:
        model_name = model.get('name') or 'semantic_model'
        lines.append(f"- model: {model_name}")

        definition = model.get('definition') or {}
        entities = definition.get('entities', {}) if isinstance(definition, dict) else {}
        if isinstance(entities, dict):
            entity_names = list(entities.keys())[:max_entities]
            if entity_names:
                lines.append(f"  entities: {', '.join(entity_names)}")

            for entity_name in entity_names:
                entity = entities.get(entity_name, {}) if isinstance(entities.get(entity_name), dict) else {}
                table_ref = entity.get('table') or entity.get('table_name') or ''
                fields = entity.get('fields', {}) if isinstance(entity.get('fields'), dict) else {}
                metrics = entity.get('metrics', {}) if isinstance(entity.get('metrics'), dict) else {}
                field_names = ', '.join(list(fields.keys())[:8]) if fields else ''
                metric_names = ', '.join(list(metrics.keys())[:8]) if metrics else ''
                parts = [f"entity {entity_name}"]
                if table_ref:
                    parts.append(f"table={table_ref}")
                if field_names:
                    parts.append(f"fields={field_names}")
                if metric_names:
                    parts.append(f"metrics={metric_names}")
                lines.append(f"  - {'; '.join(parts)}")

    return lines


def build_ai_query_context(workspace_id: Any) -> dict[str, Any]:
    try:
        workspace_int = int(str(workspace_id))
    except Exception:
        workspace_int = 1

    schema_lines = _format_schema_lines(workspace_int)
    semantic_lines = _format_semantic_lines(workspace_int)
    datasources = store.list_data_sources(workspace_int)

    sections: list[str] = []
    if schema_lines:
        sections.append('Schema Snapshot:\n' + '\n'.join(schema_lines))
    if semantic_lines:
        sections.append('Semantic Models:\n' + '\n'.join(semantic_lines))

    if not sections:
        sections.append('No schema or semantic model context is available for this workspace yet.')

    prompt_context = '\n\n'.join(sections)
    return {
        'workspace_id': workspace_int,
        'schema_tables': len(schema_lines),
        'semantic_models': len([ln for ln in semantic_lines if ln.startswith('- model:')]),
        'datasources': [
            {
                'id': d.get('id'),
                'name': d.get('name'),
                'platform': d.get('platform') or d.get('type') or 'unknown',
            }
            for d in datasources[:20]
        ],
        'prompt_context': prompt_context,
    }


def build_ai_query_context_with_runtime(
    workspace_id: Any,
    datasource_id: Any = None,
    schema_name: Any = None,
) -> dict[str, Any]:
    base = build_ai_query_context(workspace_id)
    selected_ds = None
    if datasource_id not in (None, '', '0'):
        try:
            ds_id = int(str(datasource_id))
            for item in base.get('datasources', []):
                if int(item.get('id') or 0) == ds_id:
                    selected_ds = item
                    break
        except Exception:
            selected_ds = None

    runtime_lines = []
    if selected_ds:
        runtime_lines.append(f"Datasource: {selected_ds.get('name')} ({selected_ds.get('platform')})")
    if schema_name:
        runtime_lines.append(f"Schema: {schema_name}")

    if runtime_lines:
        base['runtime_context'] = {
            'datasource': selected_ds,
            'schema': schema_name,
        }
        base['prompt_context'] = f"{' | '.join(runtime_lines)}\n\n{base.get('prompt_context', '')}"

    return base
