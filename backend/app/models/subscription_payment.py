from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class SubscriptionPayment(Base):
    __tablename__ = "subscription_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    external_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    invoice_pdf_url = Column(String, nullable=True)

    user_subscription = relationship("UserSubscription", back_populates="payments")
