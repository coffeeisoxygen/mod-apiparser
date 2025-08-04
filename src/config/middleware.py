from time import perf_counter
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from utils.mlogger import LoggerManager, logger, request_id


def setup_middlewares(app: FastAPI):
    """Cors And Middleware."""
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
        rid = request_id()
        request.state.request_id = rid
        log = logger.bind(request_id=rid)
        log.info(f"Request: {request.method} {request.url}")
        with log.contextualize():
            start = perf_counter()
            with LoggerManager.log_block(
                operation=f"HTTP {request.method} {request.url}", level="DEBUG"
            ):
                response = await call_next(request)
            duration = perf_counter() - start
        log.info(
            f"Response: {response.status_code} {request.method} {request.url} | duration={duration:.3f}s"
        )
        response.headers["X-Request-ID"] = rid
        return response
