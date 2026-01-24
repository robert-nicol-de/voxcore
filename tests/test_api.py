"""API endpoint tests"""

import pytest
from fastapi.testclient import TestClient
from voxquery.api import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get("/ready")
    
    assert response.status_code == 200
    assert response.json()["ready"] == True


def test_login_valid_credentials(client):
    """Test login with valid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "demo", "password": "demo"},
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "invalid", "password": "invalid"},
    )
    
    assert response.status_code == 401


def test_query_validation(client):
    """Test SQL validation endpoint"""
    response = client.post(
        "/api/v1/query/validate",
        params={"sql": "SELECT * FROM customers LIMIT 10"},
    )
    
    assert response.status_code == 200
    assert response.json()["valid"] == True
