import time
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.redis_client = None

        if self.settings.redis_url:
            try:
                import redis.asyncio as redis

                self.redis_client = redis.from_url(self.settings.redis_url, decode_responses=True)
            except Exception:
                self.redis_client = None

    async def _is_rate_limited_redis(self, client_ip: str) -> bool:
        if not self.redis_client:
            return False

        minute_bucket = int(time.time() // 60)
        key = f"ipam:ratelimit:{client_ip}:{minute_bucket}"

        try:
            count = await self.redis_client.incr(key)
            if count == 1:
                await self.redis_client.expire(key, 65)
            return count > self.settings.rate_limit_per_minute
        except Exception:
            return False

    def _is_rate_limited_memory(self, client_ip: str) -> bool:
        now = time.time()
        bucket = self.requests[client_ip]

        while bucket and now - bucket[0] > 60:
            bucket.popleft()

        if len(bucket) >= self.settings.rate_limit_per_minute:
            return True

        bucket.append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        limited = await self._is_rate_limited_redis(client_ip)
        if not limited:
            limited = self._is_rate_limited_memory(client_ip)

        if limited:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        response = await call_next(request)
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/health") or request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})

        return await call_next(request)


def add_security_headers(response: Response) -> Response:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
