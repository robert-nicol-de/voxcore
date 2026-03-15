import random
import yaml

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

patterns = load_yaml("voxcore/training/schema_patterns.yaml")['patterns']
variations = load_yaml("voxcore/training/libraries/entity_variations.yaml")

def generate_schema():
    pattern = random.choice(list(patterns.keys()))
    schema = {
        "schema_type": pattern,
        "tables": []
    }
    for table in patterns[pattern]["tables"]:
        name = random.choice(variations.get(table, [table]))
        schema["tables"].append({
            "name": name,
            "columns": [
                f"{name[:-1] if name.endswith('s') else name}_id",
                "created_at",
                "value"
            ]
        })
    return schema

schemas = []
for i in range(1000):
    schemas.append(generate_schema())

with open("voxcore/training/synthetic_schemas.yaml", "w") as f:
    yaml.dump({"schemas": schemas}, f)
