from collections import Counter
from .query_learning_store import _load_store


def get_similar_patterns(query: str):
    store = _load_store()

    # simple keyword match (v1)
    matches = [
        entry for entry in store
        if any(word in entry["query"].lower() for word in query.lower().split())
    ]

    return matches[-20:]  # last 20 relevant


def suggest_tables(query: str):
    matches = get_similar_patterns(query)

    table_counter = Counter()

    for m in matches:
        for t in m.get("selectedTables", []):
            table_counter[t] += 1

    return [t for t, _ in table_counter.most_common(3)]
