import pytest
from fastapi.testclient import TestClient

from backend.main import app  # adjust if your entrypoint is different

@pytest.fixture
def client():
    return TestClient(app)
