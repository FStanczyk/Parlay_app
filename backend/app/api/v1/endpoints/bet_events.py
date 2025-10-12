from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.bet_event import BetEvent
from app.models.user import User
from app.schemas.bet_event import BetEventCreate, BetEventResponse
from typing import List, Optional

router = APIRouter()


def check_referer(request: Request):
    """Check that request comes from our frontend or is a legitimate browser request"""

    referer = request.headers.get("referer")
    user_agent = request.headers.get("user-agent", "").lower()

    # Allow requests from our frontend
    if referer and "localhost:3000" in referer:
        return

    # Block everything else
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
    """Get all bet events with sport and league data - frontend only access"""
    check_referer(request)
    bet_events = (
        db.query(BetEvent)
        .options(joinedload(BetEvent.sport), joinedload(BetEvent.league))
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
    """Get bet events filtered by sport_id and/or league_id with sport and league data - frontend only access"""
    check_referer(request)
    query = db.query(BetEvent).options(
        joinedload(BetEvent.sport), joinedload(BetEvent.league)
    )

    if sport_id is not None:
        query = query.filter(BetEvent.sport_id == sport_id)

    if league_id is not None:
        query = query.filter(BetEvent.league_id == league_id)

    bet_events = query.all()
    return bet_events


@router.get("/{bet_event_id}", response_model=BetEventResponse)
def get_bet_event(
    bet_event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a specific bet event by ID with sport and league data - frontend only access"""
    check_referer(request)
    bet_event = (
        db.query(BetEvent)
        .options(joinedload(BetEvent.sport), joinedload(BetEvent.league))
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

    query = db.query(BetEvent)

    if sport_id is not None:
        query = query.filter(BetEvent.sport_id == sport_id)

    if league_id is not None:
        query = query.filter(BetEvent.league_id == league_id)

    bet_events = query.all()

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "ID",
            "Odds",
            "DateTime",
            "Sport ID",
            "League ID",
            "Home Team",
            "Away Team",
            "Event",
        ]
    )

    # Write data
    for event in bet_events:
        writer.writerow(
            [
                event.id,
                event.odds,
                event.datetime,
                event.sport_id,
                event.league_id,
                event.home_team,
                event.away_team,
                event.event,
            ]
        )

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bet_events.csv"},
    )
