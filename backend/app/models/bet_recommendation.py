from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class BetRecommendation(Base):
    __tablename__ = "bet_recommendations"

    id = Column(Integer, primary_key=True, index=True)

    bet_event_id = Column(Integer, ForeignKey("bet_events.id"), nullable=False)
    tipster_id = Column(Integer, ForeignKey("tipsters.id"), nullable=False)
