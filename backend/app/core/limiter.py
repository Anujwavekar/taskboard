from fastapi import Request
from slowapi import Limiter


def get_client_ip(request: Request) -> str:
    """On Render, the real client IP is in X-Forwarded-For; otherwise use the socket address."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=get_client_ip)