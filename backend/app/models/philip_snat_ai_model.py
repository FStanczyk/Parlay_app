from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class PhilipSnatAiModel(Base):
    __tablename__ = "philip_snat_ai_models"

    id = Column(Integer, primary_key=True, index=True)
    philip_snat_league_id = Column(
        Integer,
        ForeignKey("philip_snat_leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    last_update = Column(DateTime(timezone=True), nullable=True)

    league = relationship("PhilipSnatLeague", backref="ai_models")
