from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipsterTier(Base):
    __tablename__ = "tipster_tiers"

    id = Column(Integer, primary_key=True, index=True)
    tipster_id = Column(Integer, ForeignKey("tipsters.id"), nullable=False)
    level = Column(Integer, nullable=False, default=0)
    name = Column(String, nullable=True)
    price_monthly = Column(Numeric(10, 2), nullable=True)
    features_description = Column(Text, nullable=True)

    tipster = relationship("Tipster", back_populates="tiers")
    bet_recommendations = relationship("BetRecommendation", back_populates="tipster_tier")
    stats = relationship("TipsterTierStats", back_populates="tipster_tier", uselist=False)
    range_stats = relationship("TipsterTiersRangeStats", back_populates="tipster_tier")