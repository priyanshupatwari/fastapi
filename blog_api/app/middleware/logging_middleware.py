import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Use Python's standard logger so output integrates with any logging config.
# The name mirrors the module path for easy filtering.
logger = logging.getLogger(__name__)

# Basic configuration: log to stdout at INFO level.
# In production, swap this for a structured logging setup (e.g., structlog, loguru).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming HTTP request and its response.

    Output for each request:
        → GET  /blogs/              (request arrives)
        ← 200  GET  /blogs/  42.3ms (response dispatched)

    This middleware wraps every route handler in the app.
    It does NOT modify the request or response — it only observes.

    Registered in main.py via:
        app.add_middleware(RequestLoggingMiddleware)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # ── Before the route handler ──────────────────────────────────────
        logger.info("→ %s  %s", request.method, request.url.path)
        start = time.perf_counter()

        # Pass the request down the chain — the route handler runs inside here.
        response = await call_next(request)

        # ── After the route handler ───────────────────────────────────────
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "← %s  %s  %s  %.1fms",
            response.status_code,
            request.method,
            request.url.path,
            duration_ms,
        )

        return response
