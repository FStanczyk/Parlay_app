from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipsterTierStats(Base):
    __tablename__ = "tipster_tier_stats"

    id = Column(Integer, primary_key=True, index=True)
    tipster_id = Column(
        Integer,
        ForeignKey("tipsters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipster_tier_id = Column(
        Integer,
        ForeignKey("tipster_tiers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    total_picks = Column(Integer, nullable=False, default=0)
    total_return = Column(Integer, nullable=False, default=0)
    total_picks_won = Column(Integer, nullable=False, default=0)
    sum_odds = Column(Integer, nullable=False, default=0)
    sum_stake = Column(Float, nullable=False, default=0.0)
    picks_with_description = Column(Integer, nullable=False, default=0)

    tipster = relationship("Tipster", back_populates="tier_stats")
    tipster_tier = relationship("TipsterTier", back_populates="stats")
