import pytest
from fastapi.testclient import TestClient
from app.main import app  # Ensure this imports your FastAPI app
from sqlalchemy.orm import Session
from app.models import User
from app.services.user_service import verify_password

client = TestClient(app)

@pytest.mark.parametrize(
    "user_data",
    [
        {"username": "testuser1", "email": "test1@example.com", "password": "password123"},
        {"username": "testuser2", "email": "test2@example.com", "password": "password456"},
    ]
)
def test_create_valid_user(db_session: Session, user_data):
    """
    Test creating a valid user.
    """
    response = client.post(
        "/users/signup",
        json=user_data
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert "access_token" in data, "access_token not in response"
    assert data["token_type"] == "bearer", "Incorrect token_type"

    # Verify the user is in the database
    user_in_db = db_session.query(User).filter_by(User.email == user_data["email"]).first()
    assert user_in_db is not None, "User not found in the database"
    assert user_in_db.username == user_data["username"], "Username mismatch"
    assert user_in_db.email == user_data["email"], "Email mismatch"
    # Password should be hashed
    assert verify_password(user_data["password"], user_in_db.password) is True, "Hashed and plain passwords dont match"

def test_create_user_duplicate_email(db_session: Session):
    """
    Test creating a user with an email that's already registered.
    """
    user_data = {"username": "uniqueuser1", "email": "duplicate@example.com", "password": "password123"}
    
    # First signup should succeed
    response = client.post("/users/signup", json=user_data)
    assert response.status_code == 200, f"Unexpected status code on first signup: {response.status_code}"
    
    # Second signup with the same email should fail
    user_data_dup = {"username": "uniqueuser2", "email": "duplicate@example.com", "password": "password456"}
    response_dup = client.post("/users/signup", json=user_data_dup)
    assert response_dup.status_code == 409, f"Expected 409 Conflict, got {response_dup.status_code}"
    data_dup = response_dup.json()
    assert data_dup["detail"] == "Email is already registered", "Incorrect error detail for duplicate email"

def test_create_user_duplicate_username(db_session: Session):
    """
    Test creating a user with a username that's already taken.
    """
    user_data = {"username": "duplicateuser", "email": "unique1@example.com", "password": "password123"}
    
    # First signup should succeed
    response = client.post("/users/signup", json=user_data)
    assert response.status_code == 200, f"Unexpected status code on first signup: {response.status_code}"
    
    # Second signup with the same username should fail
    user_data_dup = {"username": "duplicateuser", "email": "unique2@example.com", "password": "password456"}
    response_dup = client.post("/users/signup", json=user_data_dup)
    assert response_dup.status_code == 409, f"Expected 409 Conflict, got {response_dup.status_code}"
    data_dup = response_dup.json()
    assert data_dup["detail"] == "Username is already registered", "Incorrect error detail for duplicate username"

@pytest.mark.parametrize(
    "user_data",
    [
        # Invalid email format
        {"username": "user3", "email": "invalidemail", "password": "password123"},
        # Short password
        {"username": "user4", "email": "user4@example.com", "password": "short"},
        # Short username
        {"username": "ab", "email": "user5@example.com", "password": "password123"},
    ]
)
def test_create_invalid_user(db_session: Session, user_data):
    """
    Test creating a user with invalid data.
    """
    response = client.post(
        "/users/signup",
        json=user_data
    )
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Error details missing in response"

def test_access_me_endpoint_logged_in(db_session: Session):
    """
    Test accessing /users/me endpoint with a valid token.
    """
    # First, create a user via signup
    user_data = {"username": "testuser_me", "email": "test_me@example.com", "password": "password123"}
    signup_response = client.post("/users/signup", json=user_data)
    assert signup_response.status_code == 200, f"Unexpected status code on signup: {signup_response.status_code}"
    token = signup_response.json()["access_token"]

    # Access /users/me with the token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Unexpected status code when accessing /users/me: {response.status_code}"
    data = response.json()
    assert data["username"] == user_data["username"], "Username mismatch in /users/me response"
    assert data["email"] == user_data["email"], "Email mismatch in /users/me response"
    assert "id" in data, "User ID missing in /users/me response"
    assert "created_at" in data, "created_at missing in /users/me response"

def test_access_me_endpoint_not_logged_in():
    """
    Test accessing /users/me endpoint without providing a token.
    """
    response = client.get("/users/me")
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    data = response.json()
    assert data["detail"] == "Not authenticated", "Incorrect error detail when not authenticated"

def test_access_me_endpoint_invalid_token():
    """
    Test accessing /users/me endpoint with an invalid token.
    """
    invalid_token = "thisis.an.invalidtoken"
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    data = response.json()
    assert data["detail"] == "Could not validate credentials", "Incorrect error detail for invalid token"

def test_access_me_endpoint_non_existing_user(db_session: Session):
    """
    Test accessing /users/me endpoint with a token for a non-existing user.
    """
    from app.config.token import create_access_token
    import uuid

    fake_user_data = {
        "id": str(uuid.uuid4()),  # Generate a random UUID
        "username": "fakeuser",
        "email": "fakeuser@example.com"
    }
    token = create_access_token(data=fake_user_data)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    data = response.json()
    assert data["detail"] == "Could not validate credentials", "Incorrect error detail for non-existing user token"