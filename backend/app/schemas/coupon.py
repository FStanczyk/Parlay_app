from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.bet_event import BetEventResponse


class CouponCreate(BaseModel):
    name: str
    bet_event_ids: List[int]


class BetEventOnCouponResponse(BaseModel):
    id: int
    coupon_id: int
    bet_event_id: int
    is_recommendation: bool
    bet_recommendation_id: Optional[int] = None
    bet_event: Optional[BetEventResponse] = None

    class Config:
        from_attributes = True


class CouponResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    bet_events: Optional[List[BetEventOnCouponResponse]] = None

    class Config:
        from_attributes = True
