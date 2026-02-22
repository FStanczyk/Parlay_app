from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, case
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.models.tipster import Tipster
from app.models.tipster_tier import TipsterTier
from app.models.bet_recommendation import BetRecommendation
from app.models.bet_event import BetEvent
from app.models.game import Game
from app.models.user import User
from app.models.user_tipster_follow import UserTipsterFollow
from app.models.tipster_main_stats import TipsterMainStats
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
    TipsterStatsResponse,
    TopExpertResponse,
    TopPickResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.get("/leaderboard", response_model=List[TopExpertResponse])
def get_top_experts(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    roi_expr = case(
        (TipsterMainStats.sum_stake > 0,
         (TipsterMainStats.total_return - TipsterMainStats.sum_stake) / TipsterMainStats.sum_stake * 100),
        else_=0.0,
    )

    results = (
        db.query(
            Tipster.id,
            User.full_name,
            User.country,
            Tipster.is_verified,
            Tipster.tag_1,
            Tipster.tag_2,
            Tipster.tag_3,
            TipsterMainStats.total_picks,
            TipsterMainStats.total_picks_won,
            roi_expr.label("roi"),
        )
        .join(User, User.id == Tipster.user_id)
        .join(TipsterMainStats, TipsterMainStats.tipster_id == Tipster.id)
        .filter(TipsterMainStats.total_picks > 0)
        .order_by(roi_expr.desc())
        .limit(limit)
        .all()
    )

    return [
        TopExpertResponse(
            id=row.id,
            full_name=row.full_name,
            country=row.country,
            is_verified=row.is_verified,
            tag_1=row.tag_1,
            tag_2=row.tag_2,
            tag_3=row.tag_3,
            total_picks=row.total_picks,
            total_picks_won=row.total_picks_won,
            roi=round(float(row.roi), 2),
        )
        for row in results
    ]


@router.get("/top-picks", response_model=List[TopPickResponse])
def get_top_picks(limit: int = Query(10, ge=1, le=50), days: int = Query(3, ge=1, le=30), db: Session = Depends(get_db)):
    from app.models.game import Game as GameModel
    cutoff = datetime.now() - timedelta(days=days)

    results = (
        db.query(
            Tipster.id.label("tipster_id"),
            User.full_name.label("tipster_name"),
            Tipster.is_verified.label("tipster_verified"),
            BetEvent.event,
            BetEvent.odds,
            GameModel.home_team,
            GameModel.away_team,
            GameModel.datetime.label("game_datetime"),
        )
        .join(BetRecommendation, BetRecommendation.tipster_id == Tipster.id)
        .join(User, User.id == Tipster.user_id)
        .join(BetEvent, BetEvent.id == BetRecommendation.bet_event_id)
        .join(GameModel, GameModel.id == BetEvent.game_id)
        .filter(
            BetEvent.result == "WIN",
            GameModel.datetime >= cutoff,
        )
        .order_by(BetEvent.odds.desc())
        .limit(limit)
        .all()
    )

    return [
        TopPickResponse(
            tipster_id=row.tipster_id,
            tipster_name=row.tipster_name,
            tipster_verified=row.tipster_verified,
            event=row.event,
            odds=float(row.odds),
            home_team=row.home_team,
            away_team=row.away_team,
            game_datetime=row.game_datetime,
        )
        for row in results
    ]


@router.get("/", response_model=List[TipsterPublicResponse])
def get_all_tipsters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    following_only: bool = Query(False),
    tag_search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("followers", regex="^(followers|appreciation|recommendations)$"),
):
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

    query = (
        db.query(
            Tipster.id,
            User.full_name,
            User.country,
            Tipster.appreciation,
            Tipster.description,
            Tipster.is_verified,
            Tipster.tag_1,
            Tipster.tag_2,
            Tipster.tag_3,
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
    )

    if following_only:
        query = query.join(
            UserTipsterFollow,
            (UserTipsterFollow.tipster_id == Tipster.id) &
            (UserTipsterFollow.user_id == current_user.id)
        )

    if tag_search:
        search_pattern = f"%{tag_search}%"
        query = query.filter(
            or_(
                Tipster.tag_1.ilike(search_pattern),
                Tipster.tag_2.ilike(search_pattern),
                Tipster.tag_3.ilike(search_pattern),
            )
        )

    if sort_by == "followers":
        query = query.order_by(func.coalesce(followers_subq.c.followers_count, 0).desc())
    elif sort_by == "appreciation":
        query = query.order_by(Tipster.appreciation.desc())
    elif sort_by == "recommendations":
        query = query.order_by(func.coalesce(recommendations_subq.c.recommendations_count, 0).desc())

    results = query.all()

    return [
        TipsterPublicResponse(
            id=row.id,
            full_name=row.full_name,
            country=row.country,
            appreciation=row.appreciation,
            description=row.description,
            is_verified=row.is_verified,
            tag_1=row.tag_1,
            tag_2=row.tag_2,
            tag_3=row.tag_3,
            followers_count=row.followers_count,
            recommendations_count=row.recommendations_count,
        )
        for row in results
    ]


@router.get("/{tipster_id}", response_model=TipsterPublicResponse)
def get_tipster_by_id(tipster_id: int, db: Session = Depends(get_db)):
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

    result = (
        db.query(
            Tipster.id,
            User.full_name,
            User.country,
            Tipster.appreciation,
            Tipster.description,
            Tipster.is_verified,
            Tipster.tag_1,
            Tipster.tag_2,
            Tipster.tag_3,
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
        .filter(Tipster.id == tipster_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipster not found"
        )

    return TipsterPublicResponse(
        id=result.id,
        full_name=result.full_name,
        country=result.country,
        appreciation=result.appreciation,
        description=result.description,
        is_verified=result.is_verified,
        tag_1=result.tag_1,
        tag_2=result.tag_2,
        tag_3=result.tag_3,
        followers_count=result.followers_count,
        recommendations_count=result.recommendations_count,
    )


@router.get("/{tipster_id}/stats", response_model=TipsterStatsResponse)
def get_tipster_stats(tipster_id: int, db: Session = Depends(get_db)):
    tipster = db.query(Tipster).filter(Tipster.id == tipster_id).first()
    if not tipster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipster not found")

    stats = db.query(TipsterMainStats).filter(TipsterMainStats.tipster_id == tipster_id).first()
    if not stats:
        return TipsterStatsResponse(
            total_picks=0,
            total_picks_won=0,
            sum_stake=0.0,
            total_return=0.0,
            sum_odds=0.0,
            picks_with_description=0,
        )
    return stats


@router.get("/following/ids", response_model=List[int])
def get_followed_tipster_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(UserTipsterFollow.tipster_id)
        .filter(UserTipsterFollow.user_id == current_user.id)
        .all()
    )
    return [row.tipster_id for row in rows]


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
        .join(BetRecommendation.bet_event)
        .join(BetEvent.game)
        .options(
            joinedload(BetRecommendation.bet_event).joinedload(BetEvent.game).joinedload(Game.league),
            joinedload(BetRecommendation.tipster_tier),
        )
        .filter(BetRecommendation.tipster_id == tipster.id)
        .order_by(Game.datetime.asc())
        .all()
    )
    return recommendations


@router.get("/{tipster_id}/recommendations", response_model=List[BetRecommendationResponse])
def get_tipster_recommendations(tipster_id: int, db: Session = Depends(get_db)):
    tipster = db.query(Tipster).filter(Tipster.id == tipster_id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tipster not found"
        )

    recommendations = (
        db.query(BetRecommendation)
        .join(BetRecommendation.bet_event)
        .join(BetEvent.game)
        .options(
            joinedload(BetRecommendation.bet_event).joinedload(BetEvent.game).joinedload(Game.league),
            joinedload(BetRecommendation.tipster_tier),
        )
        .filter(BetRecommendation.tipster_id == tipster_id)
        .order_by(Game.datetime.asc())
        .all()
    )
    return recommendations


@router.post("/{tipster_id}/follow", status_code=status.HTTP_201_CREATED)
def follow_tipster(
    tipster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.id == tipster_id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tipster not found"
        )

    if tipster.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself"
        )

    existing = (
        db.query(UserTipsterFollow)
        .filter(
            UserTipsterFollow.user_id == current_user.id,
            UserTipsterFollow.tipster_id == tipster_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already following"
        )

    follow = UserTipsterFollow(user_id=current_user.id, tipster_id=tipster_id)
    db.add(follow)
    db.commit()
    return {"detail": "Followed"}


@router.delete("/{tipster_id}/follow", status_code=status.HTTP_200_OK)
def unfollow_tipster(
    tipster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow = (
        db.query(UserTipsterFollow)
        .filter(
            UserTipsterFollow.user_id == current_user.id,
            UserTipsterFollow.tipster_id == tipster_id,
        )
        .first()
    )
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not following this tipster"
        )

    db.delete(follow)
    db.commit()
    return {"detail": "Unfollowed"}


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


@router.patch("/me/recommendations/{recommendation_id}", response_model=BetRecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_data: BetRecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    recommendation = (
        db.query(BetRecommendation)
        .join(BetRecommendation.bet_event)
        .join(BetEvent.game)
        .filter(
            BetRecommendation.id == recommendation_id,
            BetRecommendation.tipster_id == tipster.id
        )
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )

    game = recommendation.bet_event.game
    if game.datetime - timedelta(minutes=30) <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit recommendation less than 30 minutes before the event"
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

    recommendation.tipster_tier_id = recommendation_data.tipster_tier_id
    recommendation.tipster_description = recommendation_data.tipster_description
    recommendation.stake = recommendation_data.stake

    db.commit()
    db.refresh(recommendation)

    recommendation = (
        db.query(BetRecommendation)
        .options(
            joinedload(BetRecommendation.bet_event).joinedload(BetEvent.game).joinedload(Game.league),
            joinedload(BetRecommendation.tipster_tier),
        )
        .filter(BetRecommendation.id == recommendation.id)
        .first()
    )

    return recommendation


@router.delete("/me/recommendations/{recommendation_id}", status_code=status.HTTP_200_OK)
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tipster = db.query(Tipster).filter(Tipster.user_id == current_user.id).first()
    if not tipster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not a tipster"
        )

    recommendation = (
        db.query(BetRecommendation)
        .join(BetRecommendation.bet_event)
        .join(BetEvent.game)
        .filter(
            BetRecommendation.id == recommendation_id,
            BetRecommendation.tipster_id == tipster.id
        )
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )

    game = recommendation.bet_event.game
    if game.datetime - timedelta(minutes=30) <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete recommendation less than 30 minutes before the event"
        )

    db.delete(recommendation)
    db.commit()

    return {"detail": "Recommendation deleted successfully"}
