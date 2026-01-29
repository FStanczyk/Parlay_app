from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription, SubscriptionStatus
from app.models.tipster import Tipster
from app.core.security import get_current_user
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    UserSubscriptionResponse,
    UserWithSubscription,
)

router = APIRouter()


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
def get_subscription_plans(db: Session = Depends(get_db)):
    """Get all active subscription plans"""
    plans = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.sort_order)
        .all()
    )
    return plans


@router.get("/me", response_model=UserWithSubscription)
def get_current_user_with_subscription(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user with their active subscription"""
    active_subscription = (
        db.query(UserSubscription)
        .filter(
            and_(
                UserSubscription.user_id == current_user.id,
                UserSubscription.status == SubscriptionStatus.ACTIVE.value,
            )
        )
        .first()
    )

    subscription_data = None
    if active_subscription:
        plan = (
            db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.id == active_subscription.plan_id)
            .first()
        )

        plan_data = None
        if plan:
            plan_data = SubscriptionPlanResponse(
                id=plan.id,
                name=plan.name,
                price_monthly=plan.price_monthly,
                price_yearly=plan.price_yearly,
                features=plan.features,
                is_active=plan.is_active,
                sort_order=plan.sort_order,
                hierarchy_order=plan.hierarchy_order,
            )

        subscription_data = UserSubscriptionResponse(
            id=active_subscription.id,
            user_id=active_subscription.user_id,
            plan_id=active_subscription.plan_id,
            status=active_subscription.status.value,
            current_period_start=active_subscription.current_period_start,
            current_period_end=active_subscription.current_period_end,
            created_at=active_subscription.created_at,
            updated_at=active_subscription.updated_at,
            plan=plan_data,
        )

    is_expert = (
        db.query(Tipster).filter(Tipster.user_id == current_user.id).first() is not None
    )

    return UserWithSubscription(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        is_expert=is_expert,
        created_at=current_user.created_at,
        subscription=subscription_data,
    )


@router.get("/my-subscription", response_model=UserSubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's active subscription"""
    subscription = (
        db.query(UserSubscription)
        .filter(
            and_(
                UserSubscription.user_id == current_user.id,
                UserSubscription.status == SubscriptionStatus.ACTIVE.value,
            )
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
        )

    return subscription
