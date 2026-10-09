from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_addition():
    assert 2 + 3 == 6


def test_string():
    assert "FastAPI" == "FastAPI"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200