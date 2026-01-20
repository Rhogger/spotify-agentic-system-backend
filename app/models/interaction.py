from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    track_id: Mapped[str]
