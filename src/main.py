from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination

# from fastapi_pagination import add_pagination
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.bar_reports.router import router as bar_reports_router
from src.bars.router import router as bars_router
from src.config import app_configs, settings
from src.exceptions import unified_exception_handler
from src.posts.router import router as posts_router

# from src.utils import limiter


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Startup
    yield
    # Shutdown


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1/minute"],
    application_limits=["1/minute"],
)
app = FastAPI(
    **app_configs,
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight.theme": "tomorrow-night"},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


@app.get("/healthcheck", include_in_schema=True)
async def healthcheck(request: Request) -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="", tags=["Auth"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])
app.include_router(bars_router, prefix="/bars", tags=["Bars"])
app.include_router(bar_reports_router, prefix="/bar-report", tags=["Bar Reports"])

# exception handlers
app.add_exception_handler(RequestValidationError, unified_exception_handler)
app.add_exception_handler(Exception, unified_exception_handler)

add_pagination(app)
