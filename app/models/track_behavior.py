from sqlalchemy import ForeignKey, UniqueConstraint, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import enum

class InteractionType(enum.Enum):
    SKIP = "skip"
    BACK = "back"
    VIEW = "view"

class TrackBehavior(Base):
    """Contabiliza interações repetitivas (Skip, Back, View)"""
    __tablename__ = "track_behaviors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    interaction_type: Mapped[InteractionType] = mapped_column(Enum(InteractionType), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=1)

    # Garante um registro por tipo de comportamento para cada par usuário/música
    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', 'interaction_type', name='uix_user_track_behavior_type'),
    )