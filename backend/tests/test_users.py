from fastapi.testclient import TestClient
from app.main import app
from faker import Faker
from email_validator import validate_email, EmailNotValidError

fake = Faker()
client = TestClient(app)

def create_user_and_get_token():
    """Helper to create a user and retrieve an auth token."""
    password = fake.password(length=10)
    new_user = {
        "name": fake.name(),
        "email": fake.unique.email(domain="gmail.com"),
        "password": password
    }

    # Ensure the email is valid
    try:
        validated = validate_email(new_user["email"])
        new_user["email"] = validated.email  # Normalize to lowercase and valid format
    except EmailNotValidError as e:
        raise AssertionError(f"Generated invalid email: {new_user['email']}") from e

    response = client.post("/users", json=new_user)
    assert response.status_code == 200, f"User creation failed: {response.text}"

    login_data = {
        "username": new_user["email"],
        "password": password
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200, f"Authentication failed: {response.text}"
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, new_user

def test_create_user():
    headers, new_user = create_user_and_get_token()
    assert new_user["name"]
    assert new_user["email"]

def test_get_users():
    headers, _ = create_user_and_get_token()
    response = client.get("/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)