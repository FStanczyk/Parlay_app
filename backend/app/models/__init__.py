# Import all models to ensure they are registered with SQLAlchemy
from app.models.bet_event import BetEvent
from app.models.sport import Sport
from app.models.league import League
from app.models.user import User
from app.models.bet_recommendation import BetRecommendation
from app.models.tipster import Tipster
from app.models.game import Game

__all__ = [
    "BetEvent",
    "Sport",
    "League",
    "User",
    "BetRecommendation",
    "Tipster",
    "Game",
]
