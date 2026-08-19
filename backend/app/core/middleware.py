"""Middleware for rate limiting and token usage cost tracking per user/IP."""

import time
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import logger

# In-memory sliding window rate-limiter: IP/User -> (request_count, window_start_time)
RATE_LIMIT_STORE: Dict[str, Tuple[int, float]] = {}
WINDOW_SIZE_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 120

# In-memory daily token usage tracker: User -> total_token_estimate
DAILY_TOKEN_USAGE: Dict[str, int] = {}


class RateLimitAndCostMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing sliding window rate limits and tracking LLM token costs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Check rate limit
        count, window_start = RATE_LIMIT_STORE.get(client_ip, (0, now))
        if now - window_start > WINDOW_SIZE_SECONDS:
            # Reset window
            RATE_LIMIT_STORE[client_ip] = (1, now)
        else:
            if count >= MAX_REQUESTS_PER_WINDOW:
                logger.warning(
                    "Rate limit exceeded for IP %s (%d requests in 60s)", client_ip, count
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Maximum 120 requests per minute allowed."
                    },
                )
            RATE_LIMIT_STORE[client_ip] = (count + 1, window_start)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Estimate token usage if endpoint calls LLM
        path = request.url.path
        if any(
            ep in path for ep in ["/tailor-resume", "/chat/sessions", "/analyze", "/run-pipeline"]
        ):
            estimated_tokens = 450
            user_id = request.headers.get("X-User-ID", client_ip)
            DAILY_TOKEN_USAGE[user_id] = DAILY_TOKEN_USAGE.get(user_id, 0) + estimated_tokens
            logger.info(
                "LLM Endpoint '%s' executed in %d ms (Estimated Tokens: %d)",
                path,
                duration_ms,
                estimated_tokens,
            )

        return response
