import uuid
from time import perf_counter
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.mlogger import get_logger, log_performance


def setup_middlewares(app: FastAPI):
    """Cors And Middleware."""
    # Get logger for this module
    logger = get_logger(__name__)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust as needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # HTTP logging middleware with request ID and timing
    @app.middleware(middleware_type="http")
    async def log_requests(request: Request, call_next: Any):
        # Generate request ID
        rid = str(uuid.uuid4())[:8]
        request.state.request_id = rid

        # Create logger with request context
        log = logger.bind(request_id=rid)
        log.info(f"Request: {request.method} {request.url}")

        # Measure request duration
        start = perf_counter()
        response = await call_next(request)
        duration = (perf_counter() - start) * 1000  # Convert to milliseconds

        # Log response with performance metrics
        log.info(
            f"Response: {response.status_code} {request.method} {request.url} | duration={duration:.2f}ms"
        )

        # Use our modular logging performance function
        log_performance(
            operation=f"HTTP {request.method} {request.url.path}",
            duration_ms=duration,
            threshold_ms=1000.0,
            extra_context={
                "status_code": response.status_code,
                "request_id": rid,
                "method": request.method,
                "url": str(request.url),
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = rid
        return response
