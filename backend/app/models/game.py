from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class GameStatus(enum.Enum):
    PENDING = "PENDING"
    FINISHED = "FINISHED"


class GameWinner(enum.Enum):
    HOME = "HOME"
    AWAY = "AWAY"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)

    datetime = Column(DateTime, nullable=False)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    odds_api_id = Column(String, nullable=True)
    status = Column(Enum(GameStatus), nullable=True)
    winner = Column(Enum(GameWinner), nullable=True)
    home_team_score = Column(Integer, nullable=True)
    away_team_score = Column(Integer, nullable=True)
    overtime = Column(Boolean, nullable=True)
    shootout = Column(Boolean, nullable=True)

    # Relationships
    sport = relationship("Sport", back_populates="games")
    league = relationship("League", back_populates="games")
    bet_events = relationship("BetEvent", back_populates="game", cascade="all, delete-orphan")
