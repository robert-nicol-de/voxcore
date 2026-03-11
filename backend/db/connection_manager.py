import configparser
import os
from pathlib import Path
from typing import Dict, List, Mapping, Optional

from backend.db.crypto import encrypt_secret, decrypt_secret
from backend.db.connectors import (
    connect_bigquery,
    connect_mysql,
    connect_postgres,
    connect_snowflake,
    connect_sqlserver,
)


class ConnectionManager:
    def __init__(self, base_dir: Optional[str] = None):
        root = base_dir or os.getenv("VOXCORE_CONNECTIONS_ROOT", "data/companies")
        self.base_dir = Path(root)

    def _company_connections_dir(self, company_id: str) -> Path:
        return self.base_dir / str(company_id) / "connections"

    def _connection_path(self, company_id: str, connection_name: str) -> Path:
        safe_name = connection_name.strip().replace("/", "_").replace("\\", "_")
        return self._company_connections_dir(company_id) / f"{safe_name}.ini"

    def list_connections(self, company_id: str) -> List[str]:
        directory = self._company_connections_dir(company_id)
        if not directory.exists():
            return []
        return sorted([p.stem for p in directory.glob("*.ini")])

    def save_connection(self, company_id: str, connection_name: str, config: Mapping[str, str]) -> Path:
        path = self._connection_path(company_id, connection_name)
        path.parent.mkdir(parents=True, exist_ok=True)

        db_config = dict(config)
        password = str(db_config.get("password", "") or "")
        if password and not password.startswith("gAAAA"):
            db_config["password"] = encrypt_secret(password)

        parser = configparser.ConfigParser()
        parser["database"] = {k: str(v) for k, v in db_config.items() if v is not None}
        with path.open("w", encoding="utf-8") as f:
            parser.write(f)
        return path

    def load_connection(self, company_id: str, connection_name: str, decrypt_password: bool = True) -> Dict[str, str]:
        path = self._connection_path(company_id, connection_name)
        if not path.exists():
            raise FileNotFoundError(f"Connection not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path, encoding="utf-8")

        if not parser.has_section("database"):
            return {}

        data = dict(parser["database"])
        if decrypt_password and data.get("password"):
            data["password"] = decrypt_secret(data["password"])
        return data

    def get_connection(self, config: Mapping[str, str]):
        db_type = str(config.get("type", "")).strip().lower()

        if db_type == "sqlserver":
            return connect_sqlserver(config)
        if db_type in {"postgres", "postgresql"}:
            return connect_postgres(config)
        if db_type == "mysql":
            return connect_mysql(config)
        if db_type == "snowflake":
            return connect_snowflake(config)
        if db_type == "bigquery":
            return connect_bigquery(config)

        raise RuntimeError(f"Unsupported database type: {db_type}")

    def test_connection(self, config: Mapping[str, str]) -> None:
        conn = self.get_connection(config)
        try:
            conn.close()
        except Exception:
            pass
