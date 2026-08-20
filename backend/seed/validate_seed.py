import json
from collections import defaultdict
from pathlib import Path

ALLOWED_SECTIONS = {
    "featured",
    "series",
    "minisodes",
    "songs",
}

ALLOWED_LANGUAGES = {"en", "hi"}

SEED_FILE = Path(__file__).resolve().parent / "seed_shows.json"


def validate_seed():
    with open(SEED_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    issues = []

    content_language_map = defaultdict(list)

    for record in records:
        episode_id = record.get("episode_id")

        # Required fields
        required_fields = [
            "episode_id",
            "show_title",
            "slug",
            "section",
            "categories",
            "season_number",
            "episode_number",
            "episode_title",
            "language",
            "content_group",
            "status",
        ]

        for field in required_fields:
            if not record.get(field) and record.get(field) != 0:
                issues.append(
                    f"{episode_id}: missing required field '{field}'"
                )

        # Section validation
        if record.get("section") not in ALLOWED_SECTIONS:
            issues.append(
                f"{episode_id}: invalid section "
                f"'{record.get('section')}'"
            )

        # Language validation
        if record.get("language") not in ALLOWED_LANGUAGES:
            issues.append(
                f"{episode_id}: invalid language "
                f"'{record.get('language')}'"
            )

        # Published episode validation
        if record.get("status") == "published":
            if not record.get("duration_seconds"):
                issues.append(
                    f"{episode_id}: published episode has no duration"
                )

            artwork = record.get("artwork_available", [])

            required_artwork = {
                "poster",
                "banner",
                "thumbnail",
            }

            missing_artwork = required_artwork - set(artwork)

            if missing_artwork:
                issues.append(
                    f"{episode_id}: published episode missing artwork "
                    f"{sorted(missing_artwork)}"
                )

        # Track content_group + language
        key = (
            record.get("content_group"),
            record.get("language"),
        )

        content_language_map[key].append(episode_id)

    # Detect duplicate content_group + language
    for (content_group, language), episode_ids in content_language_map.items():
        if len(episode_ids) > 1:
            issues.append(
                f"Duplicate content variant: "
                f"content_group='{content_group}', "
                f"language='{language}', "
                f"episodes={episode_ids}"
            )

    print(f"Scanned {len(records)} seed records.")
    print(f"Found {len(issues)} validation issue(s).")

    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("No validation issues found.")


if __name__ == "__main__":
    validate_seed()