from typing import Mapping
import psycopg2


def connect_postgres(config: Mapping[str, str]):
    return psycopg2.connect(
        host=config.get("host", ""),
        port=int(str(config.get("port", "5432") or "5432")),
        user=config.get("username", ""),
        password=config.get("password", ""),
        database=config.get("database", ""),
        connect_timeout=int(str(config.get("timeout", "15") or "15")),
    )
