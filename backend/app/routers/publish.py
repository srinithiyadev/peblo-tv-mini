from datetime import datetime
from pathlib import Path
import json
import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Show, Season, Episode, Artwork, PublishRun


router = APIRouter(prefix="/admin", tags=["Publish"])


CATALOGUE_DIR = (
    Path(__file__).resolve().parents[2] / "published"
)

CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)

CATALOGUE_FILE = CATALOGUE_DIR / "catalogue.json"


def get_validation_issues(db: Session):
    issues = []

    episodes = (
        db.query(Episode)
        .filter(Episode.status == "published")
        .all()
    )

    seen_variants = {}

    for episode in episodes:
        key = (
            episode.content_group,
            episode.language,
        )

        if key in seen_variants:
            issues.append(
                f"{episode.episode_id}: duplicate "
                f"content_group/language"
            )
        else:
            seen_variants[key] = episode.episode_id

        if not episode.duration_seconds:
            issues.append(
                f"{episode.episode_id}: missing duration"
            )

    return issues


@router.post("/publish")
def publish_catalogue(
    db: Session = Depends(get_db),
):
    issues = get_validation_issues(db)

    if issues:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Publish blocked.",
                "issues": issues,
            },
        )

    published_episodes = (
        db.query(Episode)
        .filter(Episode.status == "published")
        .all()
    )

    catalogue = []

    for episode in published_episodes:
        season = (
            db.query(Season)
            .filter(Season.id == episode.season_id)
            .first()
        )

        show = (
            db.query(Show)
            .filter(Show.id == season.show_id)
            .first()
        )

        artworks = {
    artwork.artwork_type: (
        "/uploads/" + Path(artwork.file_path).name
    )
    for artwork in episode.artworks
}

        catalogue.append({
            "show_id": show.id,
            "show_title": show.title,
            "slug": show.slug,
            "section": show.section,
            "categories": show.categories,
            "episode_id": episode.episode_id,
            "episode_number": episode.episode_number,
            "title": episode.title,
            "duration_seconds": episode.duration_seconds,
            "language": episode.language,
            "content_group": episode.content_group,
            "artwork": artworks,
        })

    catalogue_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "episodes": catalogue,
    }

    # Atomic write:
    # write temporary file first, then replace catalogue.json.
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=CATALOGUE_DIR,
        delete=False,
    ) as temp_file:
        json.dump(
            catalogue_data,
            temp_file,
            indent=2,
            ensure_ascii=False,
        )
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_path = Path(temp_file.name)

    os.replace(temp_path, CATALOGUE_FILE)

    publish_run = PublishRun(
        user="admin",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        shows_count=len(
            {item["show_id"] for item in catalogue}
        ),
        episodes_count=len(catalogue),
        outcome="success",
    )

    db.add(publish_run)
    db.commit()

    return {
        "message": "Catalogue published successfully.",
        "episodes_count": len(catalogue),
        "catalogue_file": str(CATALOGUE_FILE),
    }
@router.get("/publish-runs")
def get_publish_runs(
    db: Session = Depends(get_db),
):
    runs = (
        db.query(PublishRun)
        .order_by(PublishRun.started_at.desc())
        .all()
    )

    return [
        {
            "id": run.id,
            "user": run.user,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "shows_count": run.shows_count,
            "episodes_count": run.episodes_count,
            "outcome": run.outcome,
        }
        for run in runs
    ]
