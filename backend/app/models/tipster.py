from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class Tipster(Base):
    __tablename__ = "tipsters"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appreciation = Column(Integer, nullable=False)
