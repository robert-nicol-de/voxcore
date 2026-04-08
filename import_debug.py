import backend
print("[DEBUG] backend module file:", backend.__file__)
import sys
print("[DEBUG] sys.path:", sys.path)
try:
    import backend.services.query_service as qs
    print("[DEBUG] query_service.py file:", qs.__file__)
except Exception as e:
    print("[DEBUG] query_service import error:", e)
try:
    import backend.services.query_service_actual as qsa
    print("[DEBUG] query_service_actual.py file:", qsa.__file__)
except Exception as e:
    print("[DEBUG] query_service_actual import error:", e)
print("[DEBUG] backend.services dir:", dir(backend.services))
