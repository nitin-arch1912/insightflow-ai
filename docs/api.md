# InsightFlow AI — API Documentation

This document describes standard conventions, headers, error structures, and available endpoints for the InsightFlow AI REST API.

---

## Standard Headers

| Header | Direction | Description |
|---|---|---|
| `X-Request-ID` | Incoming & Outgoing | Unique UUID assigned to each request. If supplied by caller, preserved for distributed tracing. |
| `Content-Type` | Both | `application/json` for standard payload operations. |

---

## Standard Error Response Format

All error responses (4xx and 5xx) adhere to a predictable RFC 7807-inspired JSON shape:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "The requested resource was not found.",
    "details": null,
    "request_id": "8fbf8e5c-0c5a-4933-bf9c-ea00e6a88b2f"
  }
}
```

### Error Fields

- `code` (`string`): Machine-readable error code (e.g., `VALIDATION_ERROR`, `NOT_FOUND`, `INTERNAL_SERVER_ERROR`).
- `message` (`string`): Human-readable summary of the error.
- `details` (`any`): Optional granular context (e.g., field-level validation errors).
- `request_id` (`string`): Corresponds with the `X-Request-ID` response header for log correlation.

### Example: Validation Error (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "body -> item_id",
        "message": "Input should be a valid integer, unable to parse string as an integer",
        "type": "int_parsing"
      }
    ],
    "request_id": "b1e9c20a-6e54-46c5-89f5-19a98ef2e22c"
  }
}
```

---

## Endpoints

### 1. Health Checks

- **GET `/health`**
  - **Summary**: Top-level probe for load balancers.
  - **Response 200**:
    ```json
    {
      "status": "ok",
      "version": "0.1.0",
      "environment": "development"
    }
    ```

- **GET `/api/v1/health`**
  - **Summary**: Versioned health check with validated response schema.
  - **Response 200**:
    ```json
    {
      "status": "ok",
      "version": "0.1.0",
      "environment": "development"
    }
    ```

---

### 2. System Info

- **GET `/api/v1/info`**
  - **Summary**: Operational metadata, server time, and uptime.
  - **Response 200**:
    ```json
    {
      "name": "InsightFlow AI",
      "version": "0.1.0",
      "environment": "development",
      "status": "operational",
      "server_time": "2026-10-29T15:00:00.123456+00:00",
      "uptime_seconds": 3600.42
    }
    ```
