from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CouponResult(enum.Enum):
    WON = "WON"
    LOST = "LOST"
    PENDING = "PENDING"
    VOID = "VOID"


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    odds = Column(Float, nullable=True)
    events = Column(Integer, nullable=True)
    result = Column(Enum(CouponResult), nullable=True)
    first_event_date = Column(DateTime(timezone=True), nullable=True)
    last_event_date = Column(DateTime(timezone=True), nullable=True)

    bet_events = relationship("BetEventOnCoupon", back_populates="coupon", cascade="all, delete-orphan")
