class RelationshipDetector:
    def detect(self, schema):
        relationships = []
        tables = list(schema.keys())
        for t1 in tables:
            for t2 in tables:
                if t1 == t2:
                    continue
                cols1 = schema[t1]["columns"]
                cols2 = schema[t2]["columns"]
                for c1 in cols1:
                    for c2 in cols2:
                        # --- MATCHING ID PATTERN ---
                        if c1["name"].lower() == c2["name"].lower():
                            if c1.get("semantic_type") == "id":
                                relationships.append({
                                    "from_table": t1,
                                    "to_table": t2,
                                    "from_column": c1["name"],
                                    "to_column": c2["name"],
                                    "type": "inferred_fk"
                                })
                        # --- STRONG SIGNAL: *_id ---
                        if c1["name"].lower().endswith("_id"):
                            base = c1["name"].lower().replace("_id", "")
                            if base in t2.lower():
                                relationships.append({
                                    "from_table": t1,
                                    "to_table": t2,
                                    "from_column": c1["name"],
                                    "to_column": f"{base}_id",
                                    "type": "name_match"
                                })
        return relationships
