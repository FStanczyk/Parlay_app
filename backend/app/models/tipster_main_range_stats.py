from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipsterMainRangeStats(Base):
    __tablename__ = "tipster_main_range_stats"
    __table_args__ = (
        UniqueConstraint("tipster_id", "range_id", name="uq_main_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tipster_id = Column(
        Integer,
        ForeignKey("tipsters.id", ondelete="CASCADE"),
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

    tipster = relationship("Tipster", back_populates="main_range_stats")
    range = relationship("TipsterRange", back_populates="main_range_stats")
