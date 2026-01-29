from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SportResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class LeagueResponse(BaseModel):
    id: int
    sport_id: int
    name: str

    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    id: int
    datetime: datetime
    sport_id: int
    league_id: int
    home_team: str
    away_team: str
    sport: Optional[SportResponse] = None
    league: Optional[LeagueResponse] = None

    class Config:
        from_attributes = True


class BetEventBase(BaseModel):
    odds: float
    game_id: int
    event: str


class BetEventCreate(BetEventBase):
    pass


class BetEventResponse(BetEventBase):
    id: int
    game: Optional[GameResponse] = None
    category_name: Optional[str] = None
    category_id: Optional[str] = None

    class Config:
        from_attributes = True
