from typing import Mapping


def connect_snowflake(config: Mapping[str, str]):
    raise RuntimeError(
        "Snowflake connector is scaffolded but not enabled in this backend runtime. "
        "Install snowflake-connector-python and implement connect_snowflake."
    )
