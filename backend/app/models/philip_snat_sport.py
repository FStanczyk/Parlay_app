from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class PhilipSnatSport(Base):
    __tablename__ = "philip_snat_sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sport = Column(String, nullable=False)

    prediction_files = relationship("PhilipSnatPredictionFile", back_populates="sport_rel")
