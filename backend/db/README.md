# VoxCore Connector Isolation Layout

Connection configs are stored per company:

- `data/companies/<company_id>/connections/<connection_name>.ini`

Example:

```ini
[database]
type = sqlserver
host = 102.206.211.24
database = AdventureWorks2022
username = voxcore_user
password = gAAAA...
driver = ODBC Driver 18 for SQL Server
encrypt = no
trust_server_certificate = yes
```

Notes:
- `password` is encrypted with Fernet when saved via `ConnectionManager`.
- Set `FERNET_KEY` in the environment for stable decryption across restarts.
- `ConnectionManager` decrypts password before opening a DB connection.
