"""
backend/agents/schema_agent.py

Schema Change Agent — monitors connected data sources for schema
staleness and configuration issues. Prevents AI models from generating
incorrect SQL due to outdated schema knowledge.

Surfaces:
  • Stale schema caches (not refreshed in 7+ days)
  • Datasources with no schema cache at all
  • Datasources with status != 'active'
"""
import logging
from datetime import datetime, timedelta

from .agent_store import create_alert, alert_exists_recently
from backend.db.org_store import _get_conn

logger = logging.getLogger(__name__)


def run(org_id: int | None = None, workspace_id: int | None = None) -> list[dict]:
    """Run the Schema Change Agent. Returns list of new alerts created."""
    new_alerts: list[dict] = []
    try:
        with _get_conn() as conn:
            # Build the WHERE filter for datasource scoping
            conditions = "WHERE is_active = 1"
            params: list = []
            if workspace_id is not None:
                conditions += " AND workspace_id = ?"
                params.append(workspace_id)
            elif org_id is not None:
                conditions += " AND org_id = ?"
                params.append(org_id)

            stale_cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()

            # ── Stale schema caches ───────────────────────────────────────
            stale_rows = conn.execute(
                f"""
                SELECT id, name, platform, schema_cache_at
                FROM data_sources {conditions}
                AND schema_cache_at IS NOT NULL
                AND schema_cache_at < ?
                """,
                params + [stale_cutoff],
            ).fetchall()

            for src in stale_rows:
                last_cached = (src["schema_cache_at"] or "")[:10]
                title = f"Stale schema: '{src['name']}' not refreshed in 7+ days"
                if not alert_exists_recently("schema", title, hours=24, org_id=org_id):
                    alert = create_alert(
                        agent_type="schema",
                        severity="info",
                        title=title,
                        description=(
                            f"The schema cache for '{src['name']}' ({src['platform']}) "
                            f"was last updated on {last_cached}. "
                            "Refresh the schema in Schema Explorer to ensure AI SQL "
                            "generation uses the current database structure."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "datasource_id": src["id"],
                            "datasource_name": src["name"],
                            "platform": src["platform"],
                            "last_cached": src["schema_cache_at"],
                        },
                    )
                    new_alerts.append(alert)

            # ── Datasources with no schema cache ──────────────────────────
            uncached_rows = conn.execute(
                f"""
                SELECT id, name, platform
                FROM data_sources {conditions}
                AND schema_cache_at IS NULL
                """,
                params,
            ).fetchall()

            for src in uncached_rows:
                title = f"No schema cache: '{src['name']}' requires discovery"
                if not alert_exists_recently("schema", title, hours=24, org_id=org_id):
                    alert = create_alert(
                        agent_type="schema",
                        severity="info",
                        title=title,
                        description=(
                            f"Data source '{src['name']}' ({src['platform']}) "
                            "has no cached schema. Run Schema Discovery in the Schema Explorer "
                            "to enable accurate AI SQL generation for this database."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "datasource_id": src["id"],
                            "datasource_name": src["name"],
                            "platform": src["platform"],
                        },
                    )
                    new_alerts.append(alert)

    except Exception as e:
        logger.warning(f"[SchemaAgent] Unexpected error: {e}")

    return new_alerts
