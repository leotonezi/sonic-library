from fastapi.testclient import TestClient
from app.main import app
from faker import Faker

fake = Faker()

client = TestClient(app)

def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_create_book():
    new_book = {
        "title": fake.sentence(nb_words=4),
        "author": fake.name(),
        "description": fake.text(max_nb_chars=100),
        "genre": "Mystery"
    }
    response = client.post("/books", json=new_book)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]
    assert data["description"] == new_book["description"]
    assert data["genre"] == new_book["genre"]