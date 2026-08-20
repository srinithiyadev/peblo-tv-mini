from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    section = Column(String(50), nullable=True)
    synopsis = Column(Text, nullable=True)
    categories = Column(JSON, nullable=False, default=list)

    seasons = relationship(
        "Season",
        back_populates="show",
        cascade="all, delete-orphan",
    )


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, ForeignKey("shows.id"), nullable=False)
    season_number = Column(Integer, nullable=False)

    show = relationship("Show", back_populates="seasons")

    episodes = relationship(
        "Episode",
        back_populates="season",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "season_number",
            name="uq_show_season",
        ),
    )


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
    episode_id = Column(String(100), unique=True, nullable=False)

    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)

    episode_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    duration_seconds = Column(Integer, nullable=True)

    language = Column(String(10), nullable=False)
    content_group = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="draft")

    season = relationship("Season", back_populates="episodes")

    artworks = relationship(
        "Artwork",
        back_populates="episode",
        cascade="all, delete-orphan",
    )


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True)

    episode_id = Column(
        Integer,
        ForeignKey("episodes.id"),
        nullable=False,
    )

    artwork_type = Column(String(30), nullable=False)
    file_path = Column(String(500), nullable=False)

    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    episode = relationship("Episode", back_populates="artworks")

    __table_args__ = (
        UniqueConstraint(
            "episode_id",
            "artwork_type",
            name="uq_episode_artwork_type",
        ),
    )


class PublishRun(Base):
    __tablename__ = "publish_runs"

    id = Column(Integer, primary_key=True)

    user = Column(String(255), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    shows_count = Column(Integer, default=0)
    episodes_count = Column(Integer, default=0)

    outcome = Column(String(30), nullable=False)