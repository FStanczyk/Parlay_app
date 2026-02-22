from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Tipster(Base):
    __tablename__ = "tipsters"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appreciation = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    tag_1 = Column(String(20), nullable=True)
    tag_2 = Column(String(20), nullable=True)
    tag_3 = Column(String(20), nullable=True)

    tiers = relationship("TipsterTier", back_populates="tipster")
    main_stats = relationship("TipsterMainStats", back_populates="tipster", uselist=False)
    tier_stats = relationship("TipsterTierStats", back_populates="tipster")
    main_range_stats = relationship("TipsterMainRangeStats", back_populates="tipster")
    tier_range_stats = relationship("TipsterTiersRangeStats", back_populates="tipster")
    tier_stats = relationship("TipsterTierStats", back_populates="tipster")
    main_range_stats = relationship("TipsterMainRangeStats", back_populates="tipster")
    tier_range_stats = relationship("TipsterTiersRangeStats", back_populates="tipster")
