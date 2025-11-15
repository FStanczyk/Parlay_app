from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.league import League
from app.schemas.league import LeagueResponse

router = APIRouter()


@router.get("/", response_model=List[LeagueResponse])
def get_leagues(sport_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get leagues with download=True from the database, optionally filtered by sport_id"""
    query = db.query(League).filter(League.download == True)
    if sport_id:
        query = query.filter(League.sport_id == sport_id)
    leagues = query.all()
    return leagues


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: int, db: Session = Depends(get_db)):
    """Get a specific league by ID"""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league
