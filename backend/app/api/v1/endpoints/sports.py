from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.core.database import get_db
from app.models.sport import Sport
from app.models.league import League
from app.schemas.sport import SportResponse

router = APIRouter()


@router.get("/", response_model=List[SportResponse])
def get_sports(db: Session = Depends(get_db)):
    """Get sports that have at least one league with download=True"""
    sports = (
        db.query(Sport)
        .join(League, Sport.id == League.sport_id)
        .filter(League.download == True)
        .distinct()
        .all()
    )
    return sports


@router.get("/{sport_id}", response_model=SportResponse)
def get_sport(sport_id: int, db: Session = Depends(get_db)):
    """Get a specific sport by ID"""
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport
