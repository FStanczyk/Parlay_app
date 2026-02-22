from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipsterTiersRangeStats(Base):
    __tablename__ = "tipster_tiers_range_stats"
    __table_args__ = (
        UniqueConstraint("tipster_tier_id", "range_id", name="uq_tier_range"),
    )

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
        index=True,
    )
    range_id = Column(
        Integer,
        ForeignKey("tipster_ranges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_picks = Column(Integer, nullable=False, default=0)
    total_return = Column(Integer, nullable=False, default=0)
    total_picks_won = Column(Integer, nullable=False, default=0)
    sum_stake = Column(Float, nullable=False, default=0.0)

    tipster = relationship("Tipster", back_populates="tier_range_stats")
    tipster_tier = relationship("TipsterTier", back_populates="range_stats")
    range = relationship("TipsterRange", back_populates="tier_range_stats")
