from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    spotify_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    artists: Mapped[str] = mapped_column(String, index=True)
    duration_ms: Mapped[int] = mapped_column(Integer)
    acousticness: Mapped[float] = mapped_column(Float)
    danceability: Mapped[float] = mapped_column(Float)
    energy: Mapped[float] = mapped_column(Float)
    instrumentalness: Mapped[float] = mapped_column(Float)
    speechiness: Mapped[float] = mapped_column(Float)
    valence: Mapped[float] = mapped_column(Float)
    explicit: Mapped[bool] = mapped_column(default=False)
    is_popular: Mapped[bool] = mapped_column(default=False)
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
