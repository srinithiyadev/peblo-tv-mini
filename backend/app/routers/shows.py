from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Show

router = APIRouter(prefix="/admin/shows", tags=["Shows"])


class ShowCreate(BaseModel):
    title: str
    slug: str
    section: str | None = None
    synopsis: str | None = None
    categories: list[str] = []


class ShowUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    section: str | None = None
    synopsis: str | None = None
    categories: list[str] | None = None


@router.get("")
def list_shows(db: Session = Depends(get_db)):
    return db.query(Show).order_by(Show.id).all()


@router.get("/{show_id}")
def get_show(show_id: int, db: Session = Depends(get_db)):
    show = db.query(Show).filter(Show.id == show_id).first()

    if not show:
        raise HTTPException(
            status_code=404,
            detail="Show not found",
        )

    return show


@router.post("", status_code=201)
def create_show(
    data: ShowCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Show)
        .filter(Show.slug == data.slug)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A show with this slug already exists.",
        )

    show = Show(
        title=data.title,
        slug=data.slug,
        section=data.section,
        synopsis=data.synopsis,
        categories=data.categories,
    )

    db.add(show)
    db.commit()
    db.refresh(show)

    return show


@router.put("/{show_id}")
def update_show(
    show_id: int,
    data: ShowUpdate,
    db: Session = Depends(get_db),
):
    show = db.query(Show).filter(Show.id == show_id).first()

    if not show:
        raise HTTPException(
            status_code=404,
            detail="Show not found",
        )

    updates = data.model_dump(exclude_unset=True)

    if "slug" in updates:
        existing = (
            db.query(Show)
            .filter(
                Show.slug == updates["slug"],
                Show.id != show_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="A show with this slug already exists.",
            )

    for field, value in updates.items():
        setattr(show, field, value)

    db.commit()
    db.refresh(show)

    return show


@router.delete("/{show_id}")
def delete_show(
    show_id: int,
    db: Session = Depends(get_db),
):
    show = db.query(Show).filter(Show.id == show_id).first()

    if not show:
        raise HTTPException(
            status_code=404,
            detail="Show not found",
        )

    db.delete(show)
    db.commit()

    return {"message": "Show deleted successfully"}