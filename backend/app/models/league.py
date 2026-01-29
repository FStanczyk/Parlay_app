from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    odds_api_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    download = Column(Boolean, nullable=False, default=False)
    # Relationships
    sport = relationship("Sport", back_populates="leagues")
    games = relationship("Game", back_populates="league")
