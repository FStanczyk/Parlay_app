from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)

    datetime = Column(DateTime, nullable=False)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)

    # Relationships
    sport = relationship("Sport", back_populates="games")
    league = relationship("League", back_populates="games")
    bet_events = relationship("BetEvent", back_populates="game")
