import json
from pathlib import Path

from app.database import SessionLocal
from app.models import Show, Season, Episode


BASE_DIR = Path(__file__).resolve().parent
SEED_FILE = BASE_DIR / "seed_shows.json"


def seed_database():
    with open(SEED_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    db = SessionLocal()

    try:
        shows = {}

        for record in records:
            slug = record["slug"]

            # Create show once
            if slug not in shows:
                show = (
                    db.query(Show)
                    .filter(Show.slug == slug)
                    .first()
                )

                if not show:
                    show = Show(
                        title=record["show_title"],
                        slug=slug,
                        section=record["section"],
                        synopsis=record["synopsis"],
                        categories=record["categories"],
                    )
                    db.add(show)
                    db.flush()

                shows[slug] = show

            show = shows[slug]

            # Create season if it doesn't exist
            season = (
                db.query(Season)
                .filter(
                    Season.show_id == show.id,
                    Season.season_number == record["season_number"],
                )
                .first()
            )

            if not season:
                season = Season(
                    show_id=show.id,
                    season_number=record["season_number"],
                )
                db.add(season)
                db.flush()

            # Create episode
            existing_episode = (
                db.query(Episode)
                .filter(
                    Episode.episode_id == record["episode_id"]
                )
                .first()
            )

            if not existing_episode:
                episode = Episode(
                    episode_id=record["episode_id"],
                    season_id=season.id,
                    episode_number=record["episode_number"],
                    title=record["episode_title"],
                    duration_seconds=record["duration_seconds"],
                    language=record["language"],
                    content_group=record["content_group"],
                    status=record["status"],
                )

                db.add(episode)

        db.commit()

        print(f"Successfully processed {len(records)} seed records.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()