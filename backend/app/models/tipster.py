from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Tipster(Base):
    __tablename__ = "tipsters"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appreciation = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    tiers = relationship("TipsterTier", back_populates="tipster")
