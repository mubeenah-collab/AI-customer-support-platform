from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.presentation.api.v1.health_router import get_health_service
from backend.src.presentation.schemas.health_schemas import ComponentHealth


def test_liveness_probe():
    client = TestClient(app)
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_probe_healthy():
    mock_service = AsyncMock()
    mock_service.get_readiness_status.return_value = (
        "healthy",
        [
            ComponentHealth(name="database", status="healthy", details="Connected"),
            ComponentHealth(name="vector_store", status="healthy", details="ChromaDB connected"),
        ],
    )

    app.dependency_overrides[get_health_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/api/v1/health/ready")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["components"]) == 2


def test_system_metrics():
    mock_service = MagicMock()
    mock_service.get_system_metrics.return_value = {
        "cpu_usage_percent": 15.5,
        "memory_usage_percent": 42.0,
        "disk_usage_percent": 30.0,
        "active_db_pool_status": "connected",
        "timestamp": 123456789.0,
    }

    app.dependency_overrides[get_health_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/api/v1/health/metrics")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["cpu_usage_percent"] == 15.5
    assert data["memory_usage_percent"] == 42.0
