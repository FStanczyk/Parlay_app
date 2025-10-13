from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BetEvent(Base):
    __tablename__ = "bet_events"

    id = Column(Integer, primary_key=True, index=True)

    odds = Column(Float, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    event = Column(String, nullable=False)

    # Relationships
    game = relationship("Game", back_populates="bet_events")
