from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from decimal import Decimal


class TipsterCreate(BaseModel):
    description: Optional[str] = None


class TipsterUpdate(BaseModel):
    description: Optional[str] = None


class TipsterTierCreate(BaseModel):
    level: int = 0
    name: str
    price_monthly: Optional[Decimal] = None
    features_description: Optional[str] = None

    @model_validator(mode='after')
    def validate_price(self):
        if self.level == 0:
            self.price_monthly = Decimal('0')
        elif self.price_monthly is None or self.price_monthly <= 0:
            raise ValueError('Price is required for non-free tiers')
        return self


class TipsterTierUpdate(BaseModel):
    level: Optional[int] = None
    name: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    features_description: Optional[str] = None


class TipsterTierResponse(BaseModel):
    id: int
    tipster_id: int
    level: int
    name: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    features_description: Optional[str] = None

    class Config:
        from_attributes = True


class TipsterResponse(BaseModel):
    id: int
    user_id: int
    description: Optional[str] = None
    appreciation: int
    is_verified: bool

    class Config:
        from_attributes = True


class TipsterPublicResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    country: Optional[str] = None
    appreciation: int
    description: Optional[str] = None
    is_verified: bool
    followers_count: int
    recommendations_count: int

    class Config:
        from_attributes = True


from datetime import datetime as dt

class GameResponse(BaseModel):
    id: int
    datetime: dt
    home_team: str
    away_team: str

    class Config:
        from_attributes = True


class BetEventResponse(BaseModel):
    id: int
    odds: float
    event: str
    game: Optional[GameResponse] = None

    class Config:
        from_attributes = True


class TipsterTierBasic(BaseModel):
    id: int
    level: int
    name: Optional[str] = None

    class Config:
        from_attributes = True


class BetRecommendationCreate(BaseModel):
    bet_event_id: int
    tipster_tier_id: Optional[int] = None
    tipster_description: Optional[str] = None
    stake: Optional[Decimal] = None

    @field_validator('stake')
    @classmethod
    def validate_stake(cls, v):
        if v is not None and v < 0:
            raise ValueError('Stake must be positive')
        return v


class BetRecommendationResponse(BaseModel):
    id: int
    bet_event_id: int
    tipster_id: int
    tipster_tier_id: Optional[int] = None
    tipster_description: Optional[str] = None
    stake: Optional[Decimal] = None
    bet_event: Optional[BetEventResponse] = None
    tipster_tier: Optional[TipsterTierBasic] = None

    class Config:
        from_attributes = True
