from pydantic import BaseModel


class LeagueResponse(BaseModel):
    id: int
    sport_id: int
    odds_api_id: str
    name: str
    country_code: str
    download: bool

    class Config:
        from_attributes = True
