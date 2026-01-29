from fastapi import APIRouter
from app.api.v1.endpoints import (
    users,
    auth,
    bet_events,
    sports,
    leagues,
    subscriptions,
    tipsters,
    games,
    coupons,
    admin,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bet_events.router, prefix="/bet-events", tags=["bet-events"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(sports.router, prefix="/sports", tags=["sports"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
api_router.include_router(
    subscriptions.router, prefix="/subscriptions", tags=["subscriptions"]
)
api_router.include_router(tipsters.router, prefix="/tipsters", tags=["tipsters"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["coupons"])
api_router.include_router(admin.router, tags=["admin"])