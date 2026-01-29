from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BetEventOnCoupon(Base):
    __tablename__ = "bet_events_on_coupons"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    bet_event_id = Column(Integer, ForeignKey("bet_events.id"), nullable=False)
    is_recommendation = Column(Boolean, default=False, nullable=False)
    bet_recommendation_id = Column(Integer, ForeignKey("bet_recommendations.id"), nullable=True)

    coupon = relationship("Coupon", back_populates="bet_events")
