from collections import defaultdict
import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])

SEED_FILE = (
    Path(__file__).resolve().parents[2]
    / "seed"
    / "seed_shows.json"
)

ALLOWED_SECTIONS = {
    "featured",
    "series",
    "minisodes",
    "songs",
}

ALLOWED_LANGUAGES = {"en", "hi"}


@router.get("/validation-report")
def validation_report():
    with open(SEED_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    issues = []

    content_language_map = defaultdict(list)

    for record in records:
        episode_id = record.get("episode_id")

        if not record.get("section"):
            issues.append({
                "episode_id": episode_id,
                "type": "missing_section",
                "message": "Section is required.",
            })

        elif record["section"] not in ALLOWED_SECTIONS:
            issues.append({
                "episode_id": episode_id,
                "type": "invalid_section",
                "message": f"Invalid section: {record['section']}",
            })

        if record.get("language") not in ALLOWED_LANGUAGES:
            issues.append({
                "episode_id": episode_id,
                "type": "invalid_language",
                "message": f"Invalid language: {record.get('language')}",
            })

        if record.get("status") == "published":
            artwork = set(record.get("artwork_available", []))

            required = {"poster", "banner", "thumbnail"}
            missing = sorted(required - artwork)

            if missing:
                issues.append({
                    "episode_id": episode_id,
                    "type": "missing_artwork",
                    "message": f"Missing artwork: {', '.join(missing)}",
                })

        key = (
            record.get("content_group"),
            record.get("language"),
        )

        content_language_map[key].append(episode_id)

    for (content_group, language), episode_ids in content_language_map.items():
        if len(episode_ids) > 1:
            issues.append({
                "type": "duplicate_content_variant",
                "content_group": content_group,
                "language": language,
                "episode_ids": episode_ids,
                "message": (
                    "Multiple episodes use the same "
                    "content_group and language."
                ),
            })

    return {
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }