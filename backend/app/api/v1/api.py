from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, bet_events, sports, leagues

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bet_events.router, prefix="/bet-events", tags=["bet-events"])
api_router.include_router(sports.router, prefix="/sports", tags=["sports"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
