from fastapi.testclient import TestClient
from app.main import app
from faker import Faker
from email_validator import validate_email, EmailNotValidError
from unittest.mock import patch

patcher = patch('app.core.mail.send_activation_email', lambda *args, **kwargs: None)
patcher.start()

fake = Faker()
client = TestClient(app)

def create_user_and_get_token():
    password = fake.password(length=10)
    new_user = {
        "name": fake.name(),
        "email": fake.unique.email(domain="gmail.com"),
        "password": password
    }

    try:
        validated = validate_email(new_user["email"])
        new_user["email"] = validated.email
    except EmailNotValidError as e:
        raise AssertionError(f"Generated invalid email: {new_user['email']}") from e

    response = client.post("/users", json=new_user)
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter_by(email=new_user["email"]).first()
    user.is_active = True
    db.commit()
    db.close()

    assert response.status_code == 200

    login_data = {
        "username": new_user["email"],
        "password": password
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_books():
    headers = create_user_and_get_token()
    response = client.get("/books", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_create_book():
    headers = create_user_and_get_token()
    new_book = {
        "title": fake.sentence(nb_words=4),
        "author": fake.name(),
        "description": fake.text(max_nb_chars=100),
        "genre": "Mystery"
    }
    response = client.post("/books", json=new_book, headers=headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]
    assert data["description"] == new_book["description"]
    assert data["genre"] == new_book["genre"]

patcher.stop()