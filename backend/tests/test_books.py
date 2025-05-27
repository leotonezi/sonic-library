from fastapi.testclient import TestClient
from app.main import app
from faker import Faker
from email_validator import validate_email, EmailNotValidError
from app.core.database import SessionLocal
from app.models.user import User

fake = Faker()
client = TestClient(app)

def create_user_and_get_cookies():
    """Helper to create a user and retrieve auth cookies."""
    password = fake.password(length=10)
    new_user = {
        "name": fake.name(),
        "email": fake.unique.email(domain="gmail.com"),
        "password": password
    }

    try:
        validated = validate_email(new_user["email"])
        new_user["email"] = validated.normalized
    except EmailNotValidError as e:
        raise AssertionError(f"Generated invalid email: {new_user['email']}") from e

    response = client.post("/users", json=new_user)
    assert response.status_code == 200, f"User creation failed: {response.text}"

    db = SessionLocal()
    user = db.query(User).filter_by(email=new_user["email"]).first()
    user.is_active = True
    db.commit()
    db.close()

    login_data = {
        "username": new_user["email"],
        "password": password
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200, f"Authentication failed: {response.text}"

    return response.cookies

def test_get_books():
    cookies = create_user_and_get_cookies()
    response = client.get("/books", cookies=cookies)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_create_book():
    cookies = create_user_and_get_cookies()
    new_book = {
        "title": fake.sentence(nb_words=4),
        "author": fake.name(),
        "description": fake.text(max_nb_chars=100),
        "genres": ["Mystery"]
    }
    response = client.post("/books", json=new_book, cookies=cookies)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]
    assert data["description"] == new_book["description"]
    assert "genres" in data
    assert isinstance(data["genres"], list)
    assert "Mystery" in data["genres"]
