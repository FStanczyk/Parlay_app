from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional


class PhilipSnatSportBase(BaseModel):
    name: str
    sport: str


class PhilipSnatSportCreate(PhilipSnatSportBase):
    pass


class PhilipSnatSportResponse(PhilipSnatSportBase):
    id: int

    class Config:
        from_attributes = True


class PhilipSnatPredictionFileBase(BaseModel):
    path: str
    name: str
    date: date
    sport_id: int


class PhilipSnatPredictionFileCreate(PhilipSnatPredictionFileBase):
    pass


class PhilipSnatPredictionFileResponse(PhilipSnatPredictionFileBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    sport: Optional[PhilipSnatSportResponse] = None

    class Config:
        from_attributes = True
