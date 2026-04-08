import requests

BASE_URL = "http://localhost:8000"

endpoints = [
    ("/docs", "GET"),
    ("/api/v1/query", "POST"),
    ("/api/v1/validate", "POST"),
    ("/api/v1/login", "POST"),
    ("/permissions/debug", "GET"),
]

def test_endpoint(path, method):
    url = BASE_URL + path
    try:
        if method == "GET":
            resp = requests.get(url)
        elif method == "POST":
            # Use dummy data for POST endpoints
            if "login" in path:
                data = {"email": "bob@bib", "password": "1234"}
            elif "query" in path:
                data = {"query": "show me revenue by region for this quarter"}
            elif "validate" in path:
                data = {"sql": "SELECT 1"}
            else:
                data = {}
            resp = requests.post(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return False
        print(f"{method} {path} -> {resp.status_code}")
        return resp.status_code < 500
    except Exception as e:
        print(f"{method} {path} -> ERROR: {e}")
        return False

def main():
    all_passed = True
    for path, method in endpoints:
        if not test_endpoint(path, method):
            all_passed = False
    if all_passed:
        print("\nAll endpoints responded successfully!")
    else:
        print("\nSome endpoints failed. Check output above.")

if __name__ == "__main__":
    main()
