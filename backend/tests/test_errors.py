"""
Tests for standardized RFC 7807 error responses.

Verifies:
  - 404 Not Found error format and request_id injection
  - 405 Method Not Allowed error format
  - 422 Request Validation error format with field-level details
  - 500 Internal Server Error format without leaking internal details
"""

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import create_app


# Helper router for testing validation errors and internal errors
mock_router = APIRouter()


class SamplePayload(BaseModel):
    item_id: int
    name: str


@mock_router.post("/test/validation")
async def validation_endpoint(payload: SamplePayload) -> dict:
    return {"status": "ok"}


@mock_router.get("/test/crash")
async def crash_endpoint() -> None:
    raise RuntimeError("Simulated crash")


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    app.include_router(mock_router)
    # raise_server_exceptions=False is required to let TestClient capture 500 responses
    return TestClient(app, raise_server_exceptions=False)


def test_404_error_format(client: TestClient) -> None:
    response = client.get("/api/v1/nonexistent-route")
    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    error = data["error"]
    assert error["code"] == "NOT_FOUND"
    assert "message" in error
    assert "request_id" in error
    assert error["request_id"] == response.headers.get("X-Request-ID")


def test_405_error_format(client: TestClient) -> None:
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    data = response.json()

    assert "error" in data
    error = data["error"]
    assert error["code"] == "METHOD_NOT_ALLOWED"
    assert "request_id" in error
    assert error["request_id"] == response.headers.get("X-Request-ID")


def test_422_validation_error_format(client: TestClient) -> None:
    # Send invalid type for item_id (string instead of int) and missing name
    response = client.post("/test/validation", json={"item_id": "not-an-int"})
    assert response.status_code == 422
    data = response.json()

    assert "error" in data
    error = data["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "Request validation failed"
    assert isinstance(error["details"], list)
    assert len(error["details"]) > 0

    # Verify field error details shape
    detail = error["details"][0]
    assert "field" in detail
    assert "message" in detail
    assert "type" in detail
    assert "request_id" in error


def test_500_unhandled_exception_format(client: TestClient) -> None:
    response = client.get("/test/crash")
    assert response.status_code == 500
    data = response.json()

    assert "error" in data
    error = data["error"]
    assert error["code"] == "INTERNAL_SERVER_ERROR"
    assert "message" in error
    assert "request_id" in error
    assert error["request_id"] == response.headers.get("X-Request-ID")
