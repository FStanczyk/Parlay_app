from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class UserTipsterFollow(Base):
    __tablename__ = "user_tipster_follows"
    __table_args__ = (
        UniqueConstraint("user_id", "tipster_id", name="uq_user_tipster_follow"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tipster_id = Column(Integer, ForeignKey("tipsters.id", ondelete="CASCADE"), nullable=False)
    followed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
