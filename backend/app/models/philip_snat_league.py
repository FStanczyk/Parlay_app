from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from app.core.database import Base


class PhilipSnatLeague(Base):
    __tablename__ = "philip_snat_leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    update = Column(Boolean, nullable=False, default=True)
    download = Column(Boolean, nullable=False, default=True)
    predict = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
