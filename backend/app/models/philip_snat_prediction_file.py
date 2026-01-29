from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PhilipSnatPredictionFile(Base):
    __tablename__ = "philip_snat_prediction_file"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    sport_id = Column(Integer, ForeignKey("philip_snat_sports.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sport_rel = relationship("PhilipSnatSport", back_populates="prediction_files")
