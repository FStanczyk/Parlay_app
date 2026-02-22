from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipsterRange(Base):
    __tablename__ = "tipster_ranges"
    __table_args__ = (
        UniqueConstraint("range_start", "range_end", name="uq_range_bounds"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    range_start = Column(Float, nullable=False)
    range_end = Column(Float, nullable=False)

    main_range_stats = relationship("TipsterMainRangeStats", back_populates="range")
    tier_range_stats = relationship("TipsterTiersRangeStats", back_populates="range")
