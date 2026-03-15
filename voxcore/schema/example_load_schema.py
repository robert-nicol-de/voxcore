"""
Example usage of the Schema Intelligence Loader.
Loads the schema model and prints the tables section.
"""
from load_schema_model import load_schema_model

if __name__ == "__main__":
    schema = load_schema_model()
    print("Loaded tables:")
    for table, info in schema["tables"].items():
        print(f"- {table}: type={info.get('type')}, columns={info.get('columns')}")
