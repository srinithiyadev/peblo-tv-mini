import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["Catalog"])

CATALOGUE_FILE = (
    Path(__file__).resolve().parents[2]
    / "published"
    / "catalogue.json"
)


def _load():
    if not CATALOGUE_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Catalogue has not been published yet.",
        )

    with open(CATALOGUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/catalog")
def get_catalog():
    return _load()


@router.get("/catalog/search")
def search_catalog(
    q: str | None = Query(None),
    category: str | None = None,
    language: str | None = None,
    section: str | None = None,
):
    data = _load()
    results = []

    for entry in data["episodes"]:
        if section and entry.get("section") != section:
            continue

        if category and category not in entry.get("categories", []):
            continue

        if language and language != entry.get("language"):
            continue

        if q:
            q_lower = q.lower()

            haystack = (
                entry.get("show_title", "").lower()
                + " "
                + entry.get("title", "").lower()
                + " "
                + " ".join(entry.get("categories", [])).lower()
            )

            if q_lower not in haystack:
                continue

        results.append(entry)

    return {
        "count": len(results),
        "results": results,
    }