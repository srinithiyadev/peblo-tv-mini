from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_catalog():
    response = client.get("/catalog")
    assert response.status_code == 200

    data = response.json()

    assert "episodes" in data
    assert isinstance(data["episodes"], list)


def test_catalog_search():
    response = client.get("/catalog/search?q=Kite")
    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
