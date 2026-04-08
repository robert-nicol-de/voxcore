import os

bad_files = [
    "query_service_actual.py",
    "query_service_v2.py"
]

base = os.path.dirname(__file__)

for f in bad_files:
    if os.path.exists(os.path.join(base, f)):
        raise RuntimeError(f"Forbidden duplicate detected: {f}")
