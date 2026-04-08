import pytest

# --- RBAC Enforcement ---
def test_rbac_block(client):
    response = client.post("/query", json={
        "text": "SELECT salary FROM employees",
        "session_id": None,
        "mode": "live",
        "user_role": "analyst"
    })
    assert response.status_code == 403

# --- Sensitive Data Masking ---
def test_masking(client):
    response = client.post("/query", json={
        "text": "SELECT email FROM users",
        "session_id": None,
        "mode": "live",
        "user_role": "analyst"
    })
    data = response.json().get("data", [{}])[0]
    assert any("***" in str(v) for v in data.values())

# --- Policy Engine ---
def test_high_risk_requires_approval(client):
    response = client.post("/query", json={
        "text": "SELECT * FROM massive_table",
        "session_id": None,
        "mode": "live",
        "user_role": "analyst"
    })
    assert response.json().get("status") == "pending"

# --- Approval Auto-Execution ---
def test_approval_flow(client):
    # Submit high-risk query
    resp = client.post("/query", json={
        "text": "SELECT * FROM massive_table",
        "session_id": None,
        "mode": "live",
        "user_role": "analyst"
    })
    approval_id = resp.json().get("approval_id")
    # Approve
    client.post(f"/api/approvals/{approval_id}/approve")
    # Get result
    result = client.get(f"/api/approvals/{approval_id}/status")
    assert result.json().get("status") == "approved"

# --- Schema Drift ---
def test_schema_drift(client):
    # Simulate schema update
    client.post("/admin/update_schema", json={"add_column": "new_column"})
    response = client.post("/query", json={
        "text": "SELECT new_column FROM table",
        "session_id": None,
        "mode": "live",
        "user_role": "admin"
    })
    assert response.status_code == 200

# --- Redaction ---
def test_redaction(client):
    response = client.post("/query", json={
        "text": "SELECT 1/0 AS error_trigger",
        "session_id": None,
        "mode": "live",
        "user_role": "admin"
    })
    error = response.json().get("error", {})
    assert "@" not in str(error.get("details", ""))
