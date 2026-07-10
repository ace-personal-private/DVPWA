from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.config import settings
from app.database import create_db_and_tables, engine

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
from app.routers import (
    admin,
    auth,
    health,
    orders,
    portfolio,
    stocks,
    support,
    uploads,
    users,
    wallet,
)
from app.seed import seed_initial_data
from app.uploads import UPLOAD_DIR


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for FastAPI application."""
    create_db_and_tables()
    with Session(engine) as session:
        seed_initial_data(session)
    yield


# VULN-CWE-209: debug=True (default in dev, since ENV defaults to
# "development") returns full HTML tracebacks to the client on unhandled
# exceptions instead of a generic error response.
app = FastAPI(title="StonksCo API", lifespan=lifespan, debug=settings.env != "production")

# VULN-CWE-942: allow_origin_regex=".*" dynamically reflects any Origin
# header while allow_credentials=True remains set, so any site can make
# credentialed cross-origin requests against this API.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR.parent), name="uploads")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(wallet.router)
app.include_router(support.router)
app.include_router(admin.router)
app.include_router(uploads.router)
