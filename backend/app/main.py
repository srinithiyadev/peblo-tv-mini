from fastapi import FastAPI

from app.routers.admin import router as admin_router
from app.routers.shows import router as shows_router
from app.routers.episodes import router as episodes_router
from app.routers.artworks import router as artworks_router
from app.routers.publish import router as publish_router
from app.routers.catalogue import router as catalogue_router
app = FastAPI(
    title="Peblo TV Mini API",
    version="1.0.0",
)
app.include_router(admin_router)
app.include_router(catalogue_router)
app.include_router(shows_router)
app.include_router(episodes_router)
app.include_router(artworks_router)
app.include_router(publish_router)


@app.get("/")
def root():
    return {"message": "Peblo TV Mini API"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "peblo-tv-api",
    }