from sqlalchemy import Column, Integer, String, Boolean, Numeric, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=False)
    features = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, nullable=False)
    hierarchy_order = Column(Integer, nullable=False)

    user_subscriptions = relationship("UserSubscription", back_populates="plan")
