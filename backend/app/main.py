from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.models import (
    User,
    BetEvent,
    Sport,
    League,
    BetRecommendation,
    Tipster,
    TipsterTier,
    Game,
    SubscriptionPlan,
    UserSubscription,
    SubscriptionPayment,
)

_is_production = settings.ENVIRONMENT == "production"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Parlay App API",
    openapi_url=None if _is_production else f"{settings.API_V1_STR}/openapi.json",
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Parlay App API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
