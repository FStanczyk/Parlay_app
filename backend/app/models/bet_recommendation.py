from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class BetRecommendation(Base):
    __tablename__ = "bet_recommendations"
    __table_args__ = (
        UniqueConstraint('tipster_id', 'bet_event_id', 'tipster_tier_id', name='uq_tipster_bet_event_tier'),
    )

    id = Column(Integer, primary_key=True, index=True)

    bet_event_id = Column(Integer, ForeignKey("bet_events.id"), nullable=False)
    tipster_id = Column(Integer, ForeignKey("tipsters.id"), nullable=False)
    tipster_tier_id = Column(Integer, ForeignKey("tipster_tiers.id"), nullable=True)
    tipster_description = Column(String(1000), nullable=True)
    stake = Column(Numeric(10, 2), nullable=True)

    # Relationships
    tipster_tier = relationship("TipsterTier", back_populates="bet_recommendations")
    bet_event = relationship("BetEvent")
