from typing import Mapping


def connect_bigquery(config: Mapping[str, str]):
    raise RuntimeError(
        "BigQuery connector is scaffolded but not enabled in this backend runtime. "
        "Install google-cloud-bigquery and implement connect_bigquery."
    )
