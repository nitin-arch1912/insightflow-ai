"""
Tests for the health endpoint.

We use FastAPI's TestClient (backed by httpx) which:
  - Creates an in-process ASGI transport — no real network calls.
  - Lets us test the full request/response cycle including middleware.
  - Runs synchronously so standard pytest (no asyncio plugin needed) works.

Run:
    pytest tests/test_health.py -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Create a fresh TestClient for this module.

    We call create_app() rather than importing the module-level `app`
    so that tests don't share state with the running server.
    """
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


# ------------------------------------------------------------------ #
# /health (root shortcut)                                              #
# ------------------------------------------------------------------ #

class TestRootHealth:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_status_is_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.json()["status"] == "ok"

    def test_version_is_present(self, client: TestClient) -> None:
        response = client.get("/health")
        assert "version" in response.json()
        assert response.json()["version"] != ""


# ------------------------------------------------------------------ #
# /api/v1/health (versioned endpoint)                                 #
# ------------------------------------------------------------------ #

class TestApiV1Health:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_status_is_ok(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert data["status"] == "ok"

    def test_version_matches_config(self, client: TestClient) -> None:
        from app.core.config import settings
        data = client.get("/api/v1/health").json()
        assert data["version"] == settings.app_version

    def test_environment_is_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert data["environment"] in ("development", "staging", "production")

    def test_database_is_connected(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert data["database"] == "connected"

    def test_response_shape(self, client: TestClient) -> None:
        """Ensure the response has exactly the documented fields."""
        data = client.get("/api/v1/health").json()
        assert set(data.keys()) == {"status", "version", "environment", "database"}


# ------------------------------------------------------------------ #
# Root redirect                                                        #
# ------------------------------------------------------------------ #

class TestRootRedirect:
    def test_redirects_to_docs(self, client: TestClient) -> None:
        # follow_redirects=False lets us inspect the redirect itself
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (301, 302, 307, 308)
        assert "/docs" in response.headers.get("location", "")


# ------------------------------------------------------------------ #
# Negative cases                                                       #
# ------------------------------------------------------------------ #

class TestNegativeCases:
    def test_unknown_route_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_wrong_method_returns_405(self, client: TestClient) -> None:
        response = client.post("/api/v1/health")
        assert response.status_code == 405
