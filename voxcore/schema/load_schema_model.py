import yaml

def load_schema_model(path="voxcore/schema/schema_model.yaml"):
    """
    Load the structured schema intelligence model from YAML.
    Args:
        path (str): Path to the schema model YAML file.
    Returns:
        dict: Schema intelligence model.
    """
    with open(path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    return schema

if __name__ == "__main__":
    schema = load_schema_model()
    print(schema["tables"])
