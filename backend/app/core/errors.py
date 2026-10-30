from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException


def _field_name(loc) -> str:
    parts = [str(p) for p in loc if p not in ("body", "query", "path")]
    return ".".join(parts) or "non_field"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors: dict[str, str] = {}
        for err in exc.errors():
            field = _field_name(err["loc"])
            message = err["msg"].removeprefix("Value error, ")
            errors.setdefault(field, message)  # keep the first message per field
        return JSONResponse(
            status_code=422,
            content={"message": "Please fix the highlighted fields", "errors": errors},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": str(exc.detail)},
            headers=exc.headers,
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"message": "Too many attempts. Please wait a minute and try again."},
        )