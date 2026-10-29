"""
Tests for system info endpoint — /api/v1/info.
"""

from datetime import datetime
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


def test_get_system_info_returns_200(client: TestClient) -> None:
    response = client.get("/api/v1/info")
    assert response.status_code == 200


def test_system_info_payload_structure(client: TestClient) -> None:
    data = client.get("/api/v1/info").json()
    assert data["name"] == settings.app_name
    assert data["version"] == settings.app_version
    assert data["environment"] == settings.app_env
    assert data["status"] == "operational"
    assert "server_time" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0

    # Ensure server_time is valid ISO format
    parsed_time = datetime.fromisoformat(data["server_time"])
    assert parsed_time is not None


def test_system_info_includes_request_id_header(client: TestClient) -> None:
    response = client.get("/api/v1/info")
    assert "X-Request-ID" in response.headers
