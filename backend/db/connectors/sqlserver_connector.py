from typing import Mapping
import pyodbc


def connect_sqlserver(config: Mapping[str, str]):
    host = config.get("host", "")
    port = str(config.get("port", "")).strip()
    server = f"{host},{port}" if host and port else host

    driver = config.get("driver", "ODBC Driver 18 for SQL Server")
    encrypt = str(config.get("encrypt", "no"))
    trust = str(config.get("trust_server_certificate", "yes"))
    timeout = int(str(config.get("timeout", "15") or "15"))

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={config.get('database', '')};"
        f"UID={config.get('username', '')};"
        f"PWD={config.get('password', '')};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
    )

    return pyodbc.connect(conn_str, timeout=timeout)
