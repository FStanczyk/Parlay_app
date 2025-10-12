from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    # Relationships
    bet_events = relationship("BetEvent", back_populates="sport")
    leagues = relationship("League", back_populates="sport")
