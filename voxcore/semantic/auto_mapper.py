def build_semantic_model(schema):
    semantic = {}

    for table, columns in schema.items():
        for col in columns:
            name = col["name"]

            if "revenue" in name.lower():
                semantic["revenue"] = {
                    "table": table,
                    "column": name,
                    "aggregation": "SUM"
                }

    return semantic
