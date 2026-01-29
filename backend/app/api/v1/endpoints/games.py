from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.game import Game
from app.models.bet_event import BetEvent
from app.models.user import User
from app.schemas.bet_event import GameResponse
from typing import List, Optional

router = APIRouter()


@router.get("/popular", response_model=List[GameResponse])
def get_popular_games(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_time = datetime.now()

    subquery = (
        db.query(
            BetEvent.game_id,
            func.count(BetEvent.id).label('bet_count')
        )
        .group_by(BetEvent.game_id)
        .subquery()
    )

    games = (
        db.query(Game)
        .options(joinedload(Game.sport), joinedload(Game.league))
        .outerjoin(subquery, Game.id == subquery.c.game_id)
        .filter(Game.datetime > current_time)
        .order_by(subquery.c.bet_count.desc().nullslast(), Game.datetime.asc())
        .limit(limit)
        .all()
    )
    return games


@router.get("/search", response_model=List[GameResponse])
def search_games(
    sport_id: Optional[int] = None,
    league_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_time = datetime.now()

    query = (
        db.query(Game)
        .options(joinedload(Game.sport), joinedload(Game.league))
        .filter(Game.datetime > current_time)
    )

    if sport_id:
        query = query.filter(Game.sport_id == sport_id)

    if league_id:
        query = query.filter(Game.league_id == league_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Game.home_team.ilike(search_term)) |
            (Game.away_team.ilike(search_term))
        )

    games = query.order_by(Game.datetime.asc()).offset(offset).limit(limit).all()
    return games
