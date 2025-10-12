from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BetEvent(Base):
    __tablename__ = "bet_events"

    id = Column(Integer, primary_key=True, index=True)

    odds = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    event = Column(String, nullable=False)

    # Relationships
    sport = relationship("Sport", back_populates="bet_events")
    league = relationship("League", back_populates="bet_events")
