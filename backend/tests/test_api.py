import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routers.catalogue import CATALOGUE_FILE


client = TestClient(app)


def setup_test_catalogue():
    CATALOGUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    test_catalogue = {
        "episodes": [
            {
                "episode_id": "test_0001",
                "show_title": "Test Show",
                "title": "The Lost Kite",
                "language": "en",
                "categories": ["kids"],
                "section": "featured",
                "status": "published",
                "duration_seconds": 300,
                "content_group": "test-show-s01e01",
            },
            {
                "episode_id": "test_0002",
                "show_title": "Test Show",
                "title": "Rain on the Roof",
                "language": "en",
                "categories": ["kids"],
                "section": "series",
                "status": "published",
                "duration_seconds": 300,
                "content_group": "test-show-s01e02",
            },
        ]
    }

    CATALOGUE_FILE.write_text(
        json.dumps(test_catalogue),
        encoding="utf-8",
    )


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_catalog():
    setup_test_catalogue()

    response = client.get("/catalog")
    assert response.status_code == 200

    data = response.json()

    assert "episodes" in data
    assert isinstance(data["episodes"], list)


def test_catalog_search():
    setup_test_catalogue()

    response = client.get("/catalog/search?q=Kite")
    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)

    assert data["count"] >= 1
    assert any(
        episode["title"] == "The Lost Kite"
        for episode in data["results"]
    )