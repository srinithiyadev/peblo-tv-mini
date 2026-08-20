import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Catalogue"])

CATALOGUE_FILE = (
    Path(__file__).resolve().parents[2]
    / "published"
    / "catalogue.json"
)


@router.get("/catalogue")
def get_catalogue():
    if not CATALOGUE_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Catalogue has not been published yet.",
        )

    with open(CATALOGUE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)