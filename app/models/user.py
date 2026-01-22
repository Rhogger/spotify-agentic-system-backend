from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str | None]
    spotify_id: Mapped[str | None]
    spotify_access_token: Mapped[str | None]
    spotify_refresh_token: Mapped[str | None]
