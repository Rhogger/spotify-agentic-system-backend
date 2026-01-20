from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    artists: Mapped[str]
    duration_ms: Mapped[int]
    acousticness: Mapped[float]
    danceability: Mapped[float]
    energy: Mapped[float]
    instrumentalness: Mapped[float]
    speechiness: Mapped[float]
    valence: Mapped[float]
    explicit: Mapped[bool]
    is_popular: Mapped[bool]
    d_1920s: Mapped[bool] = mapped_column(default=False)
    d_1930s: Mapped[bool] = mapped_column(default=False)
    d_1940s: Mapped[bool] = mapped_column(default=False)
    d_1950s: Mapped[bool] = mapped_column(default=False)
    d_1960s: Mapped[bool] = mapped_column(default=False)
    d_1970s: Mapped[bool] = mapped_column(default=False)
    d_1980s: Mapped[bool] = mapped_column(default=False)
    d_1990s: Mapped[bool] = mapped_column(default=False)
    d_2000s: Mapped[bool] = mapped_column(default=False)
    d_2010s: Mapped[bool] = mapped_column(default=False)
    d_2020s: Mapped[bool] = mapped_column(default=False)
