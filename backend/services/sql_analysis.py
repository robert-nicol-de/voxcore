import re
from typing import Dict, List


def _unique(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        val = item.strip().lower()
        if val and val not in seen:
            seen.add(val)
            result.append(val)
    return result


def _extract_query_type(sql: str) -> str:
    stripped = sql.strip().lstrip("(")
    match = re.match(r"^([a-zA-Z]+)", stripped)
    return (match.group(1).upper() if match else "UNKNOWN")


def _extract_tables(sql: str) -> List[str]:
    patterns = [
        r"\bfrom\s+([a-zA-Z_][\w\.\[\]]*)",
        r"\bjoin\s+([a-zA-Z_][\w\.\[\]]*)",
        r"\bupdate\s+([a-zA-Z_][\w\.\[\]]*)",
        r"\binto\s+([a-zA-Z_][\w\.\[\]]*)",
        r"\btable\s+([a-zA-Z_][\w\.\[\]]*)",
    ]
    found: List[str] = []
    lower_sql = sql.lower()
    for pattern in patterns:
        found.extend(re.findall(pattern, lower_sql, flags=re.IGNORECASE))
    cleaned = [t.strip("[]") for t in found]
    return _unique(cleaned)


def _extract_columns(sql: str) -> List[str]:
    # Best-effort extractor for SELECT lists and WHERE predicates.
    lower_sql = sql.lower()
    columns: List[str] = []

    select_match = re.search(r"\bselect\b(.*?)\bfrom\b", lower_sql, flags=re.IGNORECASE | re.DOTALL)
    if select_match:
        select_part = select_match.group(1)
        raw_tokens = [x.strip() for x in select_part.split(",")]
        for token in raw_tokens:
            if not token or token == "*":
                continue
            token = re.sub(r"\bas\b\s+[a-zA-Z_][\w]*", "", token, flags=re.IGNORECASE).strip()
            token = token.split(".")[-1]
            token = token.strip("[] \t\n\r")
            if token and re.match(r"^[a-zA-Z_][\w]*$", token):
                columns.append(token)

    where_tokens = re.findall(r"\b([a-zA-Z_][\w]*)\s*(=|>|<|like|in|between)\b", lower_sql, flags=re.IGNORECASE)
    columns.extend([t[0] for t in where_tokens])

    return _unique(columns)


def analyze_sql(sql: str) -> Dict[str, object]:
    query_type = _extract_query_type(sql)
    tables = _extract_tables(sql)
    columns = _extract_columns(sql)
    return {
        "query_type": query_type,
        "tables": tables,
        "columns": columns,
    }
