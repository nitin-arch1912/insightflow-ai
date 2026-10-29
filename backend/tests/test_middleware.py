"""
Tests for RequestIDMiddleware.

Verifies:
  - Every response has an X-Request-ID header.
  - The generated ID is a valid UUID.
  - Custom X-Request-ID passed by client is preserved (distributed tracing).
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


def test_response_has_request_id_header(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    req_id = response.headers["X-Request-ID"]
    # Check that it's a valid UUID
    parsed = uuid.UUID(req_id, version=4)
    assert str(parsed) == req_id


def test_custom_request_id_is_preserved(client: TestClient) -> None:
    custom_id = "custom-trace-id-12345"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


def test_sequential_requests_have_unique_ids(client: TestClient) -> None:
    resp1 = client.get("/api/v1/health")
    resp2 = client.get("/api/v1/health")
    assert resp1.headers["X-Request-ID"] != resp2.headers["X-Request-ID"]
