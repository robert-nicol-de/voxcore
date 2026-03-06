"""
VoxQuery – Platform Dialect Engine v2
=======================================
Supports: SQL Server, Snowflake, Semantic Model (live)
PostgreSQL, Redshift, BigQuery (coming soon — configs ready)

Architecture:
- Each platform has its own isolated .ini file
- Zero cross-contamination between platforms
- Adding a new platform = new .ini + one rewrite function
- Core pipeline never changes
"""

import re
import configparser
from pathlib import Path
from typing import Tuple

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

# ─────────────────────────────────────────────────────────────
# PLATFORM REGISTRY
# ─────────────────────────────────────────────────────────────

def get_platform_registry() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_DIR / "platforms.ini")
    return cfg


def is_platform_live(platform: str) -> bool:
    registry = get_platform_registry()
    if not registry.has_section(platform):
        return False
    return registry.get(platform, "status", fallback="disabled") == "live"


def get_live_platforms() -> list:
    registry = get_platform_registry()
    live = registry.get("registry_meta", "live_platforms", fallback="")
    return [p.strip() for p in live.split(",") if p.strip()]


def get_coming_soon_platforms() -> list:
    registry = get_platform_registry()
    w1 = registry.get("registry_meta", "wave_1_platforms", fallback="")
    w2 = registry.get("registry_meta", "wave_2_platforms", fallback="")
    return [p.strip() for p in (w1 + "," + w2).split(",") if p.strip()]


# ─────────────────────────────────────────────────────────────
# CONFIG LOADER
# ─────────────────────────────────────────────────────────────

def load_platform_config(platform: str) -> configparser.ConfigParser:
    config_path = CONFIG_DIR / f"{platform}.ini"
    if not config_path.exists():
        raise FileNotFoundError(
            f"No config for platform '{platform}'. Expected: {config_path}\n"
            f"Live: {get_live_platforms()} | Coming soon: {get_coming_soon_platforms()}"
        )
    cfg = configparser.ConfigParser()
    cfg.read(config_path)
    return cfg


# ─────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────────────────────

def build_system_prompt(platform: str, schema_context: str = "") -> str:
    cfg = load_platform_config(platform)
    dialect_lock = cfg.get("prompt", "dialect_lock", fallback="")
    forbidden = cfg.get("prompt", "forbidden_syntax", fallback="")
    required = cfg.get("prompt", "required_syntax", fallback="")
    top_format = cfg.get("prompt", "top_format", fallback="")
    date_format = cfg.get("prompt", "date_format", fallback="")
    limit_syntax = cfg.get("dialect", "limit_syntax", fallback="LIMIT")
    schema_req = cfg.getboolean("prompt", "schema_required", fallback=False)

    whitelist = []
    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            whitelist.append(f"  - {qualified}")

    finance_hints = []
    if cfg.has_section("finance_keywords"):
        for keyword, mapping in cfg.items("finance_keywords"):
            finance_hints.append(f"  - '{keyword}' → {mapping}")

    prompt = f"""══════════════════════════════════════════════════════
ABSOLUTE DIALECT LAW — Platform: {platform.upper()}
══════════════════════════════════════════════════════
{dialect_lock}

FORBIDDEN: {', '.join(forbidden.split(','))}
REQUIRED:  {required}

PAGINATION:
{'SELECT TOP N — NEVER use LIMIT' if limit_syntax == 'TOP' else 'LIMIT N at end — NEVER use TOP'}
Format: {top_format}

DATES: {date_format}

ALLOWED TABLES ONLY:
{chr(10).join(whitelist) if whitelist else '  (see schema)'}
{'  Schema qualification required.' if schema_req else ''}

FINANCE MAPPINGS:
{chr(10).join(finance_hints) if finance_hints else '  (use tables directly)'}

SCHEMA: {schema_context if schema_context else '(injected at runtime)'}

VIOLATION → output only: SELECT 1 AS dialect_violation_detected
══════════════════════════════════════════════════════""".strip()

    return prompt


# ─────────────────────────────────────────────────────────────
# SQL REWRITERS — one per platform
# ─────────────────────────────────────────────────────────────

def rewrite_sql(sql: str, platform: str) -> str:
    cfg = load_platform_config(platform)
    sql = sql.strip().rstrip(";").strip()

    rewriters = {
        "sqlserver": _rewrite_sqlserver,
        "snowflake": _rewrite_snowflake,
        "semantic_model": _rewrite_semantic_model,
        "postgresql": _rewrite_postgresql,
        "redshift": _rewrite_redshift,
        "bigquery": _rewrite_bigquery,
    }

    rewriter = rewriters.get(platform)
    if not rewriter:
        raise ValueError(f"No rewriter for platform '{platform}'")

    return rewriter(sql, cfg)


def _rewrite_sqlserver(sql: str, cfg: configparser.ConfigParser) -> str:
    # 1. Forbidden table check → immediate fallback
    if cfg.has_section("forbidden_tables"):
        for bad_table, _ in cfg.items("forbidden_tables"):
            if re.search(rf'\b{re.escape(bad_table)}\b', sql, re.IGNORECASE):
                return cfg.get("fallback_query", "sql", fallback="SELECT 1 AS fallback").strip()

    # 2. Capture LIMIT n before killing it
    limit_match = re.search(r'\bLIMIT\s+(\d+)\b', sql, re.IGNORECASE)
    n = int(limit_match.group(1)) if limit_match else 10
    sql = re.sub(r'\s*\bLIMIT\s+\d+\b\s*;?', '', sql, flags=re.IGNORECASE)

    # 3. Inject TOP if missing
    if not re.search(r'\bSELECT\s+TOP\b', sql, re.IGNORECASE):
        sql = re.sub(
            r'(?i)\bSELECT\b(\s+DISTINCT\b)?',
            lambda m: f"SELECT{m.group(1) or ''} TOP {n}",
            sql,
            count=1
        )

    # 4. Add ORDER BY if missing
    if re.search(r'\bTOP\b', sql, re.IGNORECASE) and \
            not re.search(r'\bORDER\s+BY\b', sql, re.IGNORECASE):
        if re.search(r'\bBALANCE\b', sql, re.IGNORECASE):
            sql += "\nORDER BY BALANCE DESC"
        elif re.search(r'\bTotalDue\b', sql, re.IGNORECASE):
            sql += "\nORDER BY TotalDue DESC"
        else:
            sql += "\nORDER BY 1 DESC"

    # 5. Schema-qualify tables
    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            sql = re.sub(
                rf'(?<!\w\.)\b{re.escape(table.upper())}\b(?!\s*\.)',
                qualified,
                sql,
                flags=re.IGNORECASE
            )

    return sql


def _rewrite_snowflake(sql: str, cfg: configparser.ConfigParser) -> str:
    top_match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', sql, re.IGNORECASE)
    n = int(top_match.group(1)) if top_match else 10
    sql = re.sub(r'(?i)\bSELECT\s+TOP\s+\d+\b', 'SELECT', sql)

    if not re.search(r'\bLIMIT\s+\d+\b', sql, re.IGNORECASE):
        sql = sql.rstrip() + f"\nLIMIT {n}"

    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            sql = re.sub(
                rf'(?<!\w\.)\b{re.escape(table.upper())}\b(?!\s*\.)',
                qualified,
                sql,
                flags=re.IGNORECASE
            )

    return sql


def _rewrite_semantic_model(sql: str, cfg: configparser.ConfigParser) -> str:
    if not re.search(r'\bLIMIT\s+\d+\b', sql, re.IGNORECASE):
        sql = sql.rstrip() + "\nLIMIT 10"

    entity_map = {
        r'\bAccounts?\b': 'Account',
        r'\bTransactions?\b': 'Transaction',
        r'\bHoldings?\b': 'Holding',
        r'\bSecurities\b': 'Security',
        r'\bPrices?\b': 'Price',
    }

    for pattern, replacement in entity_map.items():
        sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)

    return sql


def _rewrite_postgresql(sql: str, cfg: configparser.ConfigParser) -> str:
    top_match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', sql, re.IGNORECASE)
    n = int(top_match.group(1)) if top_match else 10
    sql = re.sub(r'(?i)\bSELECT\s+TOP\s+\d+\b', 'SELECT', sql)

    if not re.search(r'\bLIMIT\s+\d+\b', sql, re.IGNORECASE):
        sql = sql.rstrip() + f"\nLIMIT {n}"

    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            sql = re.sub(
                rf'(?<!\w\.)\b{re.escape(table.upper())}\b(?!\s*\.)',
                qualified,
                sql,
                flags=re.IGNORECASE
            )

    return sql


def _rewrite_redshift(sql: str, cfg: configparser.ConfigParser) -> str:
    top_match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', sql, re.IGNORECASE)
    n = int(top_match.group(1)) if top_match else 10
    sql = re.sub(r'(?i)\bSELECT\s+TOP\s+\d+\b', 'SELECT', sql)

    if not re.search(r'\bLIMIT\s+\d+\b', sql, re.IGNORECASE):
        sql = sql.rstrip() + f"\nLIMIT {n}"

    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            sql = re.sub(
                rf'(?<!\w\.)\b{re.escape(table.upper())}\b(?!\s*\.)',
                qualified,
                sql,
                flags=re.IGNORECASE
            )

    return sql


def _rewrite_bigquery(sql: str, cfg: configparser.ConfigParser) -> str:
    top_match = re.search(r'\bSELECT\s+TOP\s+(\d+)\b', sql, re.IGNORECASE)
    n = int(top_match.group(1)) if top_match else 10
    sql = re.sub(r'(?i)\bSELECT\s+TOP\s+\d+\b', 'SELECT', sql)

    if not re.search(r'\bLIMIT\s+\d+\b', sql, re.IGNORECASE):
        sql = sql.rstrip() + f"\nLIMIT {n}"

    project = cfg.get("connection", "project_id", fallback="PROJECT")
    dataset = cfg.get("connection", "dataset", fallback="DATASET")

    if cfg.has_section("whitelist_tables"):
        for table, qualified in cfg.items("whitelist_tables"):
            resolved = qualified.replace("{project}", project).replace("{dataset}", dataset)
            sql = re.sub(
                rf'(?<![`\w])\b{re.escape(table.upper())}\b(?![`\w])',
                f"`{resolved}`",
                sql,
                flags=re.IGNORECASE
            )

    return sql


# ─────────────────────────────────────────────────────────────
# VALIDATOR
# ─────────────────────────────────────────────────────────────

def validate_sql(sql: str, platform: str) -> Tuple[bool, float, list]:
    cfg = load_platform_config(platform)
    issues = []
    score = 1.0

    hard_reject_raw = cfg.get("validation", "hard_reject_keywords", fallback="")
    hard_rejects = [k.strip().upper() for k in hard_reject_raw.split(",") if k.strip()]
    threshold = cfg.getfloat("validation", "score_threshold", fallback=0.7)

    sql_upper = sql.upper()

    for keyword in hard_rejects:
        if re.search(rf'\b{re.escape(keyword)}\b', sql_upper):
            issues.append(f"HARD REJECT: '{keyword}'")
            return False, 0.0, issues

    if platform == "sqlserver":
        if re.search(r'\bLIMIT\b', sql_upper):
            issues.append("LIMIT forbidden — use TOP N")
            score -= 0.5
        if not re.search(r'\bTOP\b', sql_upper):
            issues.append("Missing TOP clause")
            score -= 0.2
        if cfg.has_section("forbidden_tables"):
            for bad_table, _ in cfg.items("forbidden_tables"):
                if bad_table.upper() in sql_upper:
                    issues.append(f"Forbidden table: {bad_table}")
                    score -= 0.4

    elif platform in ("snowflake", "postgresql", "redshift", "bigquery"):
        if re.search(r'\bSELECT\s+TOP\b', sql_upper):
            issues.append(f"TOP not valid in {platform} — use LIMIT")
            score -= 0.5

    return score >= threshold, max(score, 0.0), issues


# ─────────────────────────────────────────────────────────────
# PIPELINE ENTRY POINT
# ─────────────────────────────────────────────────────────────

def process_sql(raw_sql: str, platform: str) -> dict:
    """Call this immediately after LLM returns SQL, before execution."""
    cfg = load_platform_config(platform)
    rewritten = rewrite_sql(raw_sql, platform)
    is_valid, score, issues = validate_sql(rewritten, platform)

    fallback_used = False
    final_sql = rewritten

    if not is_valid:
        fallback_used = True
        final_sql = cfg.get("fallback_query", "sql", fallback="SELECT 1 AS fallback").strip()

    return {
        "platform": platform,
        "original_sql": raw_sql,
        "rewritten_sql": rewritten,
        "final_sql": final_sql,
        "is_valid": is_valid,
        "score": round(score, 2),
        "issues": issues,
        "fallback_used": fallback_used,
    }
