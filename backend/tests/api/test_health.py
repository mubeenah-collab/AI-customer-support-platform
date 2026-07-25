from fastapi.testclient import TestClient
from backend.src.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Customer Support Platform API"
    assert "timestamp" in data
