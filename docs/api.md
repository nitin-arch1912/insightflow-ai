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
      "environment": "development",
      "database": "connected"
    }
    ```

- **GET `/api/v1/health`**
  - **Summary**: Versioned health check with validated response schema.
  - **Response 200**:
    ```json
    {
      "status": "ok",
      "version": "0.1.0",
      "environment": "development",
      "database": "connected"
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

---

### 3. Analytics Core

All analytics calculations are deterministic and backed by validated SQL queries.

- **GET `/api/v1/analytics/overview`**
  - **Query Parameters**:
    - `start_date` (`datetime`, optional)
    - `end_date` (`datetime`, optional)
    - `region` (`string`, optional)
  - **Response 200**:
    ```json
    {
      "gross_revenue": "47535.38",
      "discount_amount": "915.00",
      "net_revenue": "46620.38",
      "total_orders": 30,
      "completed_orders": 26,
      "average_order_value": "1793.09",
      "refund_rate_percentage": 3.33,
      "active_customers": 10
    }
    ```

- **GET `/api/v1/analytics/by-category`**
  - **Query Parameters**:
    - `start_date` (`datetime`, optional)
    - `end_date` (`datetime`, optional)
  - **Response 200**:
    ```json
    {
      "items": [
        {
          "category": "Electronics",
          "revenue": "25447.15",
          "units_sold": 41,
          "order_count": 14,
          "percentage_of_total": 53.53
        }
      ],
      "total_category_revenue": "47535.38"
    }
    ```

- **GET `/api/v1/analytics/by-region`**
  - **Query Parameters**:
    - `start_date` (`datetime`, optional)
    - `end_date` (`datetime`, optional)
  - **Response 200**:
    ```json
    {
      "items": [
        {
          "region": "North America",
          "revenue": "18431.18",
          "order_count": 8,
          "customer_count": 3
        }
      ],
      "total_regional_revenue": "46620.38"
    }
    ```

- **GET `/api/v1/analytics/trends`**
  - **Query Parameters**:
    - `interval` (`"daily"` | `"weekly"`, default: `"daily"`)
    - `start_date` (`datetime`, optional)
    - `end_date` (`datetime`, optional)
  - **Response 200**:
    ```json
    {
      "interval": "daily",
      "items": [
        {
          "date": "2026-10-01",
          "gross_revenue": "2837.98",
          "net_revenue": "2787.98",
          "order_count": 1
        }
      ]
    }
    ```
