from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.tipster import Tipster
from app.models.tipster_tier import TipsterTier
from app.models.bet_recommendation import BetRecommendation
from app.models.bet_event import BetEvent
from app.models.user import User
from app.models.user_tipster_follow import UserTipsterFollow
from app.schemas.tipster import (
    TipsterCreate,
    TipsterUpdate,
    TipsterResponse,
    TipsterTierCreate,
    TipsterTierUpdate,
    TipsterTierResponse,
    BetRecommendationCreate,
    BetRecommendationResponse,
    TipsterPublicResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[TipsterPublicResponse])
def get_all_tipsters(db: Session = Depends(get_db)):
    followers_subq = (
        db.query(
            UserTipsterFollow.tipster_id,
            func.count(UserTipsterFollow.id).label("followers_count"),
        )
        .group_by(UserTipsterFollow.tipster_id)
        .subquery()
    )

    recommendations_subq = (
        db.query(
            BetRecommendation.tipster_id,
            func.count(BetRecommendation.id).label("recommendations_count"),
        )
        .group_by(BetRecommendation.tipster_id)
        .subquery()
    )

    results = (
        db.query(
            Tipster.id,
            User.full_name,
            User.country,
            Tipster.appreciation,
            Tipster.description,
            Tipster.is_verified,
            func.coalesce(followers_subq.c.followers_count, 0).label("followers_count"),
            func.coalesce(recommendations_subq.c.recommendations_count, 0).label(
                "recommendations_count"
            ),
        )
        .join(User, User.id == Tipster.user_id)
        .outerjoin(followers_subq, followers_subq.c.tipster_id == Tipster.id)
        .outerjoin(
            recommendations_subq, recommendations_subq.c.tipster_id == Tipster.id
        )
        .all()
    )

    return [
        TipsterPublicResponse(
            id=row.id,
            full_name=row.full_name,
            country=row.country,
            appreciation=row.appreciation,
            description=row.description,
            is_verified=row.is_verified,
            followers_count=row.followers_count,
            recommendations_count=row.recommendations_count,
        )
        for row in results
    ]


@router.post("/", response_model=TipsterResponse)
def create_tipster(
    tipster_data: TipsterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_tipster = (
        db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    )
    if existing_tipster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a tipster"
        )

    tipster = Tipster(
        user_id=current_user.id,
        description=tipster_data.description,
        appreciation=0,
        is_verified=False,
    )
    db.add(tipster)
    db.commit()
    db.refresh(tipster)
    return tipster


@router.get("/me", response_model=TipsterResponse)
def get_my_tipster(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )
    return tipster


@router.patch("/me", response_model=TipsterResponse)
def update_my_tipster(
    tipster_data: TipsterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    if tipster_data.description is not None:
        tipster.description = tipster_data.description
    if tipster_data.tag_1 is not None:
        tipster.tag_1 = tipster_data.tag_1
    if tipster_data.tag_2 is not None:
        tipster.tag_2 = tipster_data.tag_2
    if tipster_data.tag_3 is not None:
        tipster.tag_3 = tipster_data.tag_3

    db.commit()
    db.refresh(tipster)
    return tipster


@router.get("/me/tiers", response_model=List[TipsterTierResponse])
def get_my_tiers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    tiers = (
        db.query(TipsterTier)
        .filter(TipsterTier.tipster_id == tipster.id)
        .order_by(TipsterTier.level)
        .all()
    )
    return tiers


@router.post("/me/tiers", response_model=TipsterTierResponse)
def create_tier(
    tier_data: TipsterTierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    tier = TipsterTier(
        tipster_id=tipster.id,
        level=tier_data.level,
        name=tier_data.name,
        price_monthly=tier_data.price_monthly,
        features_description=tier_data.features_description,
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@router.patch("/me/tiers/{tier_id}", response_model=TipsterTierResponse)
def update_tier(
    tier_id: int,
    tier_data: TipsterTierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    tier = (
        db.query(TipsterTier)
        .filter(TipsterTier.id == tier_id, TipsterTier.tipster_id == tipster.id)
        .first()
    )
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found"
        )

    if tier_data.level is not None:
        tier.level = tier_data.level
    if tier_data.name is not None:
        tier.name = tier_data.name
    if tier_data.price_monthly is not None:
        tier.price_monthly = tier_data.price_monthly
    if tier_data.features_description is not None:
        tier.features_description = tier_data.features_description

    final_level = tier.level
    if final_level == 0:
        tier.price_monthly = 0
    elif tier.price_monthly is None or tier.price_monthly <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price is required for non-free tiers",
        )

    db.commit()
    db.refresh(tier)
    return tier


@router.get("/me/recommendations", response_model=List[BetRecommendationResponse])
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    recommendations = (
        db.query(BetRecommendation)
        .options(
            joinedload(BetRecommendation.bet_event).joinedload(BetEvent.game),
            joinedload(BetRecommendation.tipster_tier),
        )
        .filter(BetRecommendation.tipster_id == tipster.id)
        .all()
    )
    return recommendations


@router.post("/me/recommendations", response_model=BetRecommendationResponse)
def create_recommendation(
    recommendation_data: BetRecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    bet_event = db.query(BetEvent).filter(BetEvent.id == recommendation_data.bet_event_id).first()
    if not bet_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bet event not found"
        )

    if recommendation_data.tipster_tier_id:
        tier = (
            db.query(TipsterTier)
            .filter(
                TipsterTier.id == recommendation_data.tipster_tier_id,
                TipsterTier.tipster_id == tipster.id
            )
            .first()
        )
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tier"
            )

    existing = (
        db.query(BetRecommendation)
        .filter(
            BetRecommendation.tipster_id == tipster.id,
            BetRecommendation.bet_event_id == recommendation_data.bet_event_id,
            BetRecommendation.tipster_tier_id == recommendation_data.tipster_tier_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already exists for this bet event and tier"
        )

    recommendation = BetRecommendation(
        bet_event_id=recommendation_data.bet_event_id,
        tipster_id=tipster.id,
        tipster_tier_id=recommendation_data.tipster_tier_id,
        tipster_description=recommendation_data.tipster_description,
        stake=recommendation_data.stake,
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    recommendation = (
        db.query(BetRecommendation)
        .options(
            joinedload(BetRecommendation.bet_event).joinedload(BetEvent.game),
            joinedload(BetRecommendation.tipster_tier),
        )
        .filter(BetRecommendation.id == recommendation.id)
        .first()
    )

    return recommendation
