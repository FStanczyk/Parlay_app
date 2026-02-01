from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.core.config import settings
from app.models.bet_event import BetEvent
from app.models.game import Game
from app.models.user import User
from app.schemas.bet_event import BetEventCreate, BetEventResponse
from typing import List, Optional
from urllib.parse import urlparse

router = APIRouter()


def check_referer(request: Request):
    """Check that request comes from our frontend or is a legitimate browser request"""
    referer = request.headers.get("referer")
    origin = request.headers.get("origin")

    if not referer and not origin:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    allowed_origins = settings.BACKEND_CORS_ORIGINS

    if origin:
        if origin in allowed_origins:
            return
        parsed_origin = urlparse(origin)
        origin_domain = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        if origin_domain in allowed_origins:
            return

    if referer:
        parsed_referer = urlparse(referer)
        referer_domain = f"{parsed_referer.scheme}://{parsed_referer.netloc}"
        if referer_domain in allowed_origins:
            return
        for allowed in allowed_origins:
            if allowed in referer:
                return

    raise HTTPException(
        status_code=403,
        detail="Access denied.",
    )


@router.get("/test")
def test_endpoint():
    """Simple test endpoint to debug connection issues"""
    return {"message": "Test endpoint working", "status": "ok"}


@router.get("/", response_model=List[BetEventResponse])
def get_bet_events(request: Request, db: Session = Depends(get_db)):
    """Get all bet events with game, sport and league data - frontend only access"""
    check_referer(request)
    current_time = datetime.now()
    bet_events = (
        db.query(BetEvent)
        .options(
            joinedload(BetEvent.game).joinedload(Game.sport),
            joinedload(BetEvent.game).joinedload(Game.league),
        )
        .join(Game)
        .filter(Game.datetime > current_time)
        .all()
    )
    return bet_events


@router.get("/filter", response_model=List[BetEventResponse])
def get_bet_events_by_filters(
    request: Request,
    sport_id: Optional[int] = None,
    league_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get bet events filtered by sport_id and/or league_id with game, sport and league data - frontend only access"""
    check_referer(request)
    current_time = datetime.now()
    query = db.query(BetEvent).options(
        joinedload(BetEvent.game).joinedload(Game.sport),
        joinedload(BetEvent.game).joinedload(Game.league),
    )

    # Always join Game table and filter out past events
    query = query.join(Game).filter(Game.datetime > current_time)

    if sport_id is not None:
        query = query.filter(Game.sport_id == sport_id)

    if league_id is not None:
        query = query.filter(Game.league_id == league_id)

    bet_events = query.all()
    return bet_events


@router.get("/random", response_model=List[BetEventResponse])
def get_random_bet_events(
    request: Request,
    limit: int = 10,
    sport_id: Optional[int] = None,
    league_id: Optional[int] = None,
    min_odds: Optional[float] = None,
    max_odds: Optional[float] = None,
    exclude_ids: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get N random bet events with game, sport and league data - frontend only access"""
    check_referer(request)
    current_time = datetime.now()

    is_authenticated = current_user is not None

    # Allow higher limits for authenticated users, or reasonable limits for unauthenticated users
    if not is_authenticated:
        if limit > 10:  # Allow up to 10 events for unauthenticated users
            limit = 10
        if min_odds is not None or max_odds is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Advanced filters require authentication",
            )
        if from_date is not None or to_date is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Date filters require authentication",
            )

    # Parse date filters
    from_datetime = None
    to_datetime = None

    if from_date:
        try:
            from_datetime = datetime.fromisoformat(from_date)
        except ValueError:
            from_datetime = None

    if to_date:
        try:
            # Add end of day time to include the entire day
            to_datetime = datetime.fromisoformat(to_date)
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            to_datetime = None

    # Debug logging
    print(
        f"Random endpoint called with: sport_id={sport_id}, league_id={league_id}, min_odds={min_odds}, max_odds={max_odds}, from_date={from_date}, to_date={to_date}, limit={limit}"
    )

    # Build base query with joins and time filter
    query = (
        db.query(BetEvent)
        .options(
            joinedload(BetEvent.game).joinedload(Game.sport),
            joinedload(BetEvent.game).joinedload(Game.league),
        )
        .join(Game)
    )

    # Apply date filters
    if from_datetime and to_datetime:
        # Both dates provided - filter by date range
        query = query.filter(
            Game.datetime >= from_datetime, Game.datetime <= to_datetime
        )
    elif from_datetime:
        # Only from_date provided - filter from date onwards
        query = query.filter(Game.datetime >= from_datetime)
    elif to_datetime:
        # Only to_date provided - filter up to date
        query = query.filter(Game.datetime <= to_datetime)
    else:
        # No date filters - only show future events
        query = query.filter(Game.datetime > current_time)

    # Apply additional filters
    if sport_id is not None:
        query = query.filter(Game.sport_id == sport_id)

    if league_id is not None:
        query = query.filter(Game.league_id == league_id)

    if min_odds is not None:
        query = query.filter(BetEvent.odds >= min_odds)

    if max_odds is not None:
        query = query.filter(BetEvent.odds <= max_odds)

    # Exclude specific event IDs if provided
    if exclude_ids:
        try:
            exclude_list = [
                int(id.strip()) for id in exclude_ids.split(",") if id.strip()
            ]
            if exclude_list:
                query = query.filter(~BetEvent.id.in_(exclude_list))
        except ValueError:
            # If parsing fails, ignore the exclude_ids parameter
            pass

    # Get random events using database-level randomization
    bet_events = query.order_by(func.random()).limit(limit).all()

    # Debug logging
    print(f"Query returned {len(bet_events)} events")
    for event in bet_events:
        print(
            f"Event {event.id}: Game {event.game_id}, League {event.game.league_id if event.game else 'None'}"
        )

    return bet_events


@router.get("/by-game/{game_id}", response_model=List[BetEventResponse])
def get_bet_events_for_game(
    game_id: int,
    db: Session = Depends(get_db),
):
    """Get all bet events for a specific game"""
    bet_events = (
        db.query(BetEvent)
        .options(
            joinedload(BetEvent.game).joinedload(Game.sport),
            joinedload(BetEvent.game).joinedload(Game.league),
        )
        .filter(BetEvent.game_id == game_id)
        .all()
    )
    return bet_events


@router.get("/{bet_event_id}", response_model=BetEventResponse)
def get_bet_event(
    bet_event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a specific bet event by ID with game, sport and league data - frontend only access"""
    check_referer(request)
    bet_event = (
        db.query(BetEvent)
        .options(
            joinedload(BetEvent.game).joinedload(Game.sport),
            joinedload(BetEvent.game).joinedload(Game.league),
        )
        .filter(BetEvent.id == bet_event_id)
        .first()
    )
    if bet_event is None:
        raise HTTPException(status_code=404, detail="Bet event not found")
    return bet_event


@router.post("/", response_model=BetEventResponse)
def create_bet_event(
    bet_event: BetEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new bet event - requires authentication"""
    db_bet_event = BetEvent(**bet_event.dict())
    db.add(db_bet_event)
    db.commit()
    db.refresh(db_bet_event)
    return db_bet_event


@router.get("/export/csv")
def export_bet_events_csv(
    sport_id: Optional[int] = None,
    league_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export bet events to CSV - requires authentication"""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    current_time = datetime.now()
    query = db.query(BetEvent).options(
        joinedload(BetEvent.game).joinedload(Game.sport),
        joinedload(BetEvent.game).joinedload(Game.league),
    )

    # Always join Game table and filter out past events
    query = query.join(Game).filter(Game.datetime > current_time)

    if sport_id is not None:
        query = query.filter(Game.sport_id == sport_id)

    if league_id is not None:
        query = query.filter(Game.league_id == league_id)

    bet_events = query.all()

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "ID",
            "Odds",
            "Event",
            "Game ID",
            "DateTime",
            "Sport ID",
            "League ID",
            "Home Team",
            "Away Team",
        ]
    )

    # Write data
    for event in bet_events:
        writer.writerow(
            [
                event.id,
                event.odds,
                event.event,
                event.game_id,
                event.game.datetime,
                event.game.sport_id,
                event.game.league_id,
                event.game.home_team,
                event.game.away_team,
            ]
        )

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bet_events.csv"},
    )
