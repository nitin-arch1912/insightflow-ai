"""
Request-ID middleware.

Every HTTP request gets a unique identifier that:
  - Appears in the response header `X-Request-ID`.
  - Is injected into all log messages during that request.
  - Can be used by the frontend to report errors ("request X failed").
  - Enables distributed tracing when the caller passes their own ID.

How it works:
  1. Before the handler runs: check if the client sent `X-Request-ID`.
     If yes, reuse it. If no, generate a new UUID4.
  2. Store the request_id in `request.state` so handlers can access it.
  3. After the handler runs: add the `X-Request-ID` header to the response.

Usage in a handler:
    @router.get("/example")
    async def example(request: Request):
        request_id = request.state.request_id
        ...
"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a unique request ID to every request/response cycle.

    The middleware uses Starlette's BaseHTTPMiddleware, which wraps
    the ASGI call and gives us a simple request/response interface.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # ---------------------------------------------------------- #
        # 1. Get or generate request ID                                #
        # ---------------------------------------------------------- #
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store on request.state so handlers and exception handlers
        # can access it without passing it through every function.
        request.state.request_id = request_id

        # ---------------------------------------------------------- #
        # 2. Log the incoming request                                  #
        # ---------------------------------------------------------- #
        logger.info(
            "Request started: %s %s [%s]",
            request.method,
            request.url.path,
            request_id,
        )

        # ---------------------------------------------------------- #
        # 3. Call the actual route handler                              #
        # ---------------------------------------------------------- #
        response = await call_next(request)

        # ---------------------------------------------------------- #
        # 4. Attach request ID to response headers                     #
        # ---------------------------------------------------------- #
        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            "Request completed: %s %s → %s [%s]",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
        )

        return response
