from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class SubscriptionPlanBase(BaseModel):
    name: str
    price_monthly: Decimal
    price_yearly: Decimal
    features: Dict[str, Any]
    is_active: bool = True
    sort_order: int
    hierarchy_order: int


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int

    class Config:
        from_attributes = True


class UserSubscriptionBase(BaseModel):
    plan_id: int
    status: str
    current_period_start: datetime
    current_period_end: datetime


class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    current_period_start: datetime
    current_period_end: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plan: Optional[SubscriptionPlanResponse] = None

    class Config:
        from_attributes = True


class UserWithSubscription(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    is_expert: bool = False
    created_at: datetime
    subscription: Optional[UserSubscriptionResponse] = None

    class Config:
        from_attributes = True
