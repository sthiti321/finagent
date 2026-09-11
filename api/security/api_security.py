# ============================================================
# FINAGENT API SECURITY
# C3 — API SECURITY
# ============================================================

import os
import time
import logging

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address


# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------

logger = logging.getLogger("finagent.security")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


# ------------------------------------------------------------
# RATE LIMITING
# ------------------------------------------------------------

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        "100/minute"
    ]
)


# ------------------------------------------------------------
# REQUEST SIZE LIMIT
# ------------------------------------------------------------

MAX_REQUEST_SIZE = int(
    os.getenv("FINAGENT_MAX_REQUEST_SIZE", str(1024 * 1024))
)


async def check_request_size(request: Request):
    """
    Reject requests larger than the configured maximum size.

    Default:
        1 MB
    """

    content_length = request.headers.get("content-length")

    if content_length:
        try:
            size = int(content_length)

            if size > MAX_REQUEST_SIZE:
                logger.warning(
                    "Request rejected because of excessive size | "
                    "IP=%s | size=%s",
                    get_remote_address(request),
                    size
                )

                raise HTTPException(
                    status_code=413,
                    detail="Request payload too large"
                )

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid Content-Length header"
            )


# ------------------------------------------------------------
# SECURITY HEADERS
# ------------------------------------------------------------

async def add_security_headers(request: Request, call_next):

    start_time = time.time()

    response = await call_next(request)

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Control browser referrer information
    response.headers["Referrer-Policy"] = "no-referrer"

    # Restrict browser permissions
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )


    

    # Prevent caching of sensitive API responses
    if request.url.path.startswith("/customers"):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate"
        )
        response.headers["Pragma"] = "no-cache"

    duration = time.time() - start_time

    logger.info(
        "API request | method=%s | path=%s | status=%s | "
        "duration=%.3fs | ip=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration,
        get_remote_address(request)
    )

    return response


# ------------------------------------------------------------
# HTTP METHOD SECURITY
# ------------------------------------------------------------

ALLOWED_METHODS = {
    "GET",
    "POST",
    "OPTIONS",
    "PATCH",
}


async def validate_http_method(request: Request):

    if request.method not in ALLOWED_METHODS:

        logger.warning(
            "HTTP method rejected | method=%s | path=%s | ip=%s",
            request.method,
            request.url.path,
            get_remote_address(request)
        )

        raise HTTPException(
            status_code=405,
            detail="HTTP method not allowed"
        )


# ------------------------------------------------------------
# GENERIC API ERROR HANDLER
# ------------------------------------------------------------

def sanitize_error_message(exc: Exception) -> str:
    """
    Prevent internal implementation details from being
    exposed through API error messages.
    """

    logger.exception(
        "Unhandled API exception: %s",
        exc
    )

    return "Internal server error"
