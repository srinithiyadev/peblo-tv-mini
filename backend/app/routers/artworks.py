from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Artwork, Episode


router = APIRouter(
    prefix="/admin/episodes",
    tags=["Artwork"],
)

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ARTWORK_SPECS = {
    "poster": {
        "width": 600,
        "height": 900,
        "ratio": 2 / 3,
    },
    "banner": {
        "width": 1280,
        "height": 720,
        "ratio": 16 / 9,
    },
    "thumbnail": {
        "width": 640,
        "height": 360,
        "ratio": 16 / 9,
    },
}

MAX_FILE_SIZE = 200 * 1024

@router.get("/{episode_id}/artwork")
def list_artwork(
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

    return episode.artworks


@router.post("/{episode_id}/artwork")
async def upload_artwork(
    episode_id: int,
    artwork_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if artwork_type not in ARTWORK_SPECS:
        raise HTTPException(
            status_code=400,
            detail="Artwork type must be poster, banner, or thumbnail.",
        )

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

    data = await file.read()

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be 200 KB or smaller.",
        )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    temp_path = UPLOAD_DIR / f"temp_{uuid.uuid4().hex}"

    try:
        temp_path.write_bytes(data)

        try:
            image = Image.open(temp_path)
            image.verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid image.",
            )

        image = Image.open(temp_path)

        width, height = image.size
        spec = ARTWORK_SPECS[artwork_type]

        actual_ratio = width / height

        if abs(actual_ratio - spec["ratio"]) > 0.02:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{artwork_type} must use a "
                    f"{spec['width']}x{spec['height']} aspect ratio."
                ),
            )

        filename = (
            f"{episode.episode_id}_"
            f"{artwork_type}_"
            f"{uuid.uuid4().hex}.jpg"
        )

        final_path = UPLOAD_DIR / filename
        final_path.write_bytes(data)

        existing = (
            db.query(Artwork)
            .filter(
                Artwork.episode_id == episode.id,
                Artwork.artwork_type == artwork_type,
            )
            .first()
        )

        if existing:
            existing.file_path = str(final_path)
            existing.width = width
            existing.height = height
            existing.file_size_bytes = len(data)
        else:
            artwork = Artwork(
                episode_id=episode.id,
                artwork_type=artwork_type,
                file_path=str(final_path),
                width=width,
                height=height,
                file_size_bytes=len(data),
            )
            db.add(artwork)

        db.commit()

        return {
            "message": "Artwork uploaded successfully.",
            "episode_id": episode.id,
            "artwork_type": artwork_type,
            "width": width,
            "height": height,
            "file_size_bytes": len(data),
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()