from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BetResult(enum.Enum):
    WIN = "WIN"
    LOOSE = "LOOSE"
    TO_RESOLVE = "TO_RESOLVE"
    VOID = "VOID"
    UNKNOWN = "UNKNOWN"


class BetEvent(Base):
    __tablename__ = "bet_events"

    id = Column(Integer, primary_key=True, index=True)

    odds = Column(Float, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    event = Column(String, nullable=False)
    result = Column(Enum(BetResult), nullable=True)
    odds_api_id = Column(String, nullable=True)
    category_name = Column(String, nullable=True)
    category_id = Column(String, nullable=True)

    # Relationships
    game = relationship("Game", back_populates="bet_events")
