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

    return response.cookies, new_user

def test_create_user():
    cookies, new_user = create_user_and_get_cookies()
    assert new_user["name"]
    assert new_user["email"]

def test_get_users():
    cookies, _ = create_user_and_get_cookies()
    response = client.get("/users", cookies=cookies)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)