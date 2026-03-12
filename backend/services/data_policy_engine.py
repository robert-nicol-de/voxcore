import re


SENSITIVE_COLUMNS = [
    "password",
    "ssn",
    "social_security_number",
    "credit_card",
    "credit_card_number",
    "salary",
    "private_key",
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "bank_account",
    "routing_number",
    "email",
]


def get_sensitive_columns() -> list[str]:
    return list(SENSITIVE_COLUMNS)


def find_sensitive_columns_in_query(query: str, additional_columns: list[str] | None = None) -> list[str]:
    lower_query = (query or "").lower()
    columns = list(SENSITIVE_COLUMNS)
    if additional_columns:
        columns.extend(str(column).strip().lower() for column in additional_columns if str(column).strip())

    matches: list[str] = []
    for column in columns:
        if re.search(rf"\b{re.escape(column)}\b", lower_query):
            matches.append(column)

    return sorted(set(matches))
