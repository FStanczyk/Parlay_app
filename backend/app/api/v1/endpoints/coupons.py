from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.coupon import Coupon
from app.models.bet_event import BetEvent
from app.models.bet_event_on_coupon import BetEventOnCoupon
from app.models.game import Game
from app.schemas.coupon import CouponCreate, CouponResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon_data: CouponCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not coupon_data.name or not coupon_data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon name is required"
        )

    if not coupon_data.bet_event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one bet event is required",
        )

    bet_events = (
        db.query(BetEvent).filter(BetEvent.id.in_(coupon_data.bet_event_ids)).all()
    )

    if len(bet_events) != len(coupon_data.bet_event_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more bet events not found",
        )

    try:
        total_odds = 1.0
        game_dates = []
        for be in bet_events:
            total_odds *= be.odds if be.odds else 1.0
            game = db.query(Game).filter(Game.id == be.game_id).first()
            if game and game.datetime:
                game_dates.append(game.datetime)

        game_dates.sort()

        coupon = Coupon(
            user_id=current_user.id,
            name=coupon_data.name.strip(),
            odds=round(total_odds, 2),
            events=len(bet_events),
            first_event_date=game_dates[0] if game_dates else None,
            last_event_date=game_dates[-1] if game_dates else None,
        )
        db.add(coupon)
        db.flush()

        for bet_event_id in coupon_data.bet_event_ids:
            bet_event_on_coupon = BetEventOnCoupon(
                coupon_id=coupon.id, bet_event_id=bet_event_id, is_recommendation=False
            )
            db.add(bet_event_on_coupon)

        db.commit()
        db.refresh(coupon)

        coupon.bet_events = (
            db.query(BetEventOnCoupon)
            .filter(BetEventOnCoupon.coupon_id == coupon.id)
            .all()
        )

        return coupon
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating coupon: {str(e)}",
        )


@router.get("/", response_model=List[CouponResponse])
def get_my_coupons(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    coupons = (
        db.query(Coupon)
        .filter(Coupon.user_id == current_user.id)
        .order_by(Coupon.created_at.desc())
        .all()
    )

    for coupon in coupons:
        bet_events_on_coupon = (
            db.query(BetEventOnCoupon)
            .filter(BetEventOnCoupon.coupon_id == coupon.id)
            .all()
        )

        for bet_event_on_coupon in bet_events_on_coupon:
            bet_event = (
                db.query(BetEvent)
                .options(
                    joinedload(BetEvent.game).joinedload(Game.sport),
                    joinedload(BetEvent.game).joinedload(Game.league),
                )
                .filter(BetEvent.id == bet_event_on_coupon.bet_event_id)
                .first()
            )
            if bet_event:
                bet_event_on_coupon.bet_event = bet_event

        coupon.bet_events = bet_events_on_coupon

    return coupons
