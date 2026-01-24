from sqlalchemy import ForeignKey, UniqueConstraint, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import enum

class TrackPreference(Base):
    """Armazena se o usuário gostou ou não da música (Relação 1:1)"""
    __tablename__ = "track_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    liked: Mapped[bool] = mapped_column(default=True) # True = Like, False = Dislike

    # Garante que um usuário só tenha um registro de preferência por música
    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', name='uix_user_track_preference'),
    )