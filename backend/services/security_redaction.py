import re


_URL_CREDENTIALS_PATTERN = re.compile(r"://([^:@/\s]+):([^@/\s]+)@", re.IGNORECASE)
_ODBC_PWD_PATTERN = re.compile(r"(PWD\s*=\s*)([^;\s]+)", re.IGNORECASE)
_PASSWORD_KV_PATTERN = re.compile(r"((?:password|passwd|pwd)\s*[=:]\s*)([^,;\s]+)", re.IGNORECASE)


def redact_sensitive_text(text: str) -> str:
    if not text:
        return text

    redacted = _URL_CREDENTIALS_PATTERN.sub(r"://\1:***@", text)
    redacted = _ODBC_PWD_PATTERN.sub(r"\1***", redacted)
    redacted = _PASSWORD_KV_PATTERN.sub(r"\1***", redacted)
    return redacted


def sanitize_exception_message(exc: Exception) -> str:
    return redact_sensitive_text(str(exc))