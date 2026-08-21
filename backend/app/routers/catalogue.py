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

    for sec_name, entries in data["sections"].items():
        if section and sec_name != section:
            continue

        for entry in entries:
            if category and category not in entry["categories"]:
                continue

            if language and language not in {
                lang["language"] for lang in entry["languages"]
            }:
                continue

            if q:
                q_lower = q.lower()

                haystack = (
                    entry["show_title"].lower()
                    + " "
                    + entry["title"].lower()
                    + " "
                    + " ".join(entry["categories"]).lower()
                )

                if q_lower not in haystack:
                    continue

            results.append(entry)

    return {
        "count": len(results),
        "results": results,
    }