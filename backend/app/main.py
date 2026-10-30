from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.limiter import limiter
from app.routers import auth, health

app = FastAPI(title="TaskBoard API")

app.state.limiter = limiter
register_error_handlers(app)

allowed_origins = {settings.client_url.rstrip("/"), "http://localhost:5173"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(auth.router)