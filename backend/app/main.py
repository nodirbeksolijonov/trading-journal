from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import stats, trades


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fine for the MVP; switch to Alembic migrations before moving to Postgres.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Trading Journal API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trades.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
