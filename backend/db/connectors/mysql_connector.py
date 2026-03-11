from typing import Mapping


def connect_mysql(config: Mapping[str, str]):
    raise RuntimeError(
        "MySQL connector is scaffolded but not enabled. Install a MySQL driver "
        "(for example pymysql or mysqlclient) and implement connect_mysql."
    )
