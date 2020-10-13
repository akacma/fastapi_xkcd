from fastapi.testclient import TestClient
import config
import main
from main import app, get_comic_data_by_id
from pathlib import Path


client = TestClient(app)

TEST_DIR = "tests"
TEST_IMAGES_DIR = "test_images"
TEST_RATE_LIMIT = "1/minute"


def get_settings_override():
    return config.Settings(images=f"{TEST_DIR}/{TEST_IMAGES_DIR}", rate_limit=TEST_RATE_LIMIT)


main.app.dependency_overrides[main.get_settings] = get_settings_override


def test_fetch_comics_data_by_id():
    response = client.get("comics/1000")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1000",
        "description": "Thank you for making me feel less alone.",
        "date": "12-01-06",
        "title": "1000 comics",
        "url": "https://imgs.xkcd.com/comics/1000_comics.png"
    }


def test_fetch_comics_data_by_id_with_nonnumeric_id():
    response = client.get("comics/c")
    assert response.status_code == 422
    assert response.json()[
        "detail"][0]["msg"] == "value is not a valid integer"


def test_fetch_comics_data_by_id_with_nonexistent_id():
    response = client.get("comics/10000")
    assert response.status_code == 404
    assert response.json() == {"detail": "For comic id=10000: Item not found"}


def test_fetch_many_comics_with_repeated_ids():
    response = client.get(
        "comics/many?comic_ids=10&comic_ids=5&comic_ids=10")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "5", "description":
            "Blown into prime factors",
            "date": "06-01-01",
            "title": "blown apart",
            "url": "https://imgs.xkcd.com/comics/blownapart_color.jpg"
        },
        {
            "id": "10",
            "description": "My most famous drawing, and one of the first I did for the site",
            "date": "06-01-01",
            "title": "pi equals",
            "url": "https://imgs.xkcd.com/comics/pi.jpg"
        }
    ]


def test_fetch_many_comics_with_nonexistent_id():
    response = client.get("comics/many?comic_ids=11&comic_ids=20000")
    assert response.status_code == 404
    assert response.json() == {"detail": "For comic id=20000: Item not found"}


def test_comics_download():
    response = client.get("comics/download?comic_ids=2&comic_ids=2137")
    assert response.status_code == 200
    assert (Path() / TEST_DIR / TEST_IMAGES_DIR / "2.jpg").exists() == True
    assert (Path() / TEST_DIR / TEST_IMAGES_DIR / "2137.png").exists() == True

    # deleting the downloaded images:
    path = Path() / TEST_DIR / TEST_IMAGES_DIR
    paths = [p.unlink() for p in path.iterdir()]


def test_comics_download_nonexistent_id():
    response = client.get("comics/download?comic_ids=10000")
    assert response.status_code == 404
    assert (Path() / TEST_DIR / TEST_IMAGES_DIR /
            "10000.png").exists() == False
    assert response.json() == {"detail": "For comic id=10000: Item not found"}


# this test fails
def test_fetch_many_comics_with_rate_limit_exceeded():
    response = client.get("comics/many?comic_ids=1&comic_ids=5&comic_ids=2")
    response = client.get(
        "comics/many?comic_ids=3&comic_ids=5&comic_ids=4")
    assert response.status_code == 429
