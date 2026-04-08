def build_semantic_model(schema):
    semantic = {
        "metrics": {},
        "dimensions": {},
        "time_columns": {},
        "tables": {}
    }

    for table, data in schema.items():
        semantic["tables"][table] = table

        for col in data["columns"]:
            name = col["name"]
            stype = col["semantic_type"]

            if stype == "metric":
                semantic["metrics"][name.lower()] = {
                    "table": table,
                    "column": name,
                    "aggregation": "SUM"
                }

            elif stype == "dimension":
                semantic["dimensions"][name.lower()] = {
                    "table": table,
                    "column": name
                }

            elif stype == "time":
                semantic["time_columns"][name.lower()] = {
                    "table": table,
                    "column": name
                }

    return semantic
