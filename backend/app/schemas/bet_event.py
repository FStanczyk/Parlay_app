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


class BetEventBase(BaseModel):
    odds: float
    datetime: datetime
    sport_id: int
    league_id: int
    home_team: str
    away_team: str
    event: str


class BetEventCreate(BetEventBase):
    pass


class BetEventResponse(BetEventBase):
    id: int
    sport: Optional[SportResponse] = None
    league: Optional[LeagueResponse] = None

    class Config:
        from_attributes = True
