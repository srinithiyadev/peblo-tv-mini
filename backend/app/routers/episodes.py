from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Episode, Season

router = APIRouter(prefix="/admin/episodes", tags=["Episodes"])


class EpisodeCreate(BaseModel):
    episode_id: str
    season_id: int
    episode_number: int
    title: str
    duration_seconds: int | None = None
    language: str
    content_group: str
    status: str = "draft"


class EpisodeUpdate(BaseModel):
    episode_number: int | None = None
    title: str | None = None
    duration_seconds: int | None = None
    language: str | None = None
    content_group: str | None = None
    status: str | None = None


def validate_episode(data, db, episode_id=None):
    if data.language not in {"en", "hi"}:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'en' or 'hi'.",
        )

    if data.status not in {"draft", "published"}:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'draft' or 'published'.",
        )

    if data.status == "published" and not data.duration_seconds:
        raise HTTPException(
            status_code=400,
            detail="A published episode must have a duration.",
        )

    season = (
        db.query(Season)
        .filter(Season.id == data.season_id)
        .first()
    )

    if not season:
        raise HTTPException(
            status_code=404,
            detail="Season not found.",
        )

    return season


@router.get("")
def list_episodes(db: Session = Depends(get_db)):
    return (
        db.query(Episode)
        .order_by(Episode.id)
        .all()
    )


@router.get("/{episode_id}")
def get_episode(
    episode_id: int,
    db: Session = Depends(get_db),
):
    episode = (
        db.query(Episode)
        .filter(Episode.id == episode_id)
        .first()
    )

    if not episode:
        raise HTTPException(
            status_code=404,
            detail="Episode not found.",
        )

    return episode


@router.post("", status_code=201)
def create_episode(
    data: EpisodeCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Episode)
        .filter(Episode.episode_id == data.episode_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Episode ID already exists.",
        )

    validate_episode(data, db)

    episode = Episode(
        episode_id=data.episode_id,
        season_id=data.season_id,
        episode_number=data.episode_number,
        title=data.title,
        duration_seconds=data.duration_seconds,
        language=data.language,
        content_group=data.content_group,
        status=data.status,
    )

    db.add(episode)
    db.commit()
    db.refresh(episode)

    return episode


@router.put("/{episode_id}")
def update_episode(
    episode_id: int,
    data: EpisodeUpdate,
    db: Session = Depends(get_db),
):
    episode = (
        db.query(Episode)
        .filter(Episode.id == episode_id)
        .first()
    )

    if not episode:
        raise HTTPException(
            status_code=404,
            detail="Episode not found.",
        )

    updates = data.model_dump(exclude_unset=True)

    new_language = updates.get(
        "language",
        episode.language,
    )

    new_status = updates.get(
        "status",
        episode.status,
    )

    new_duration = updates.get(
        "duration_seconds",
        episode.duration_seconds,
    )

    if new_language not in {"en", "hi"}:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'en' or 'hi'.",
        )

    if new_status not in {"draft", "published"}:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'draft' or 'published'.",
        )

    if new_status == "published" and not new_duration:
        raise HTTPException(
            status_code=400,
            detail="A published episode must have a duration.",
        )

    for field, value in updates.items():
        setattr(episode, field, value)

    db.commit()
    db.refresh(episode)

    return episode


@router.delete("/{episode_id}")
def delete_episode(
    episode_id: int,
    db: Session = Depends(get_db),
):
    episode = (
        db.query(Episode)
        .filter(Episode.id == episode_id)
        .first()
    )

    if not episode:
        raise HTTPException(
            status_code=404,
            detail="Episode not found.",
        )

    db.delete(episode)
    db.commit()

    return {"message": "Episode deleted successfully."}