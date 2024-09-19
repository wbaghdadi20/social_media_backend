import pytest
from fastapi.testclient import TestClient
from app.main import app  # Ensure this imports your FastAPI app
from sqlalchemy.orm import Session

client = TestClient(app)

def test_login_existing_user(db_session: Session):
    """
    Test logging in with an existing user.
    """
    # First, create a user via /users/signup
    user_data = {"username": "testloginuser", "email": "testlogin@example.com", "password": "password123"}
    signup_response = client.post("/users/signup", json=user_data)
    assert signup_response.status_code == 200, f"Unexpected status code on signup: {signup_response.status_code}"
    
    # Now, attempt to login with the same credentials
    login_data = {"username": "testloginuser", "email": "testlogin@example.com", "password": "password123"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Unexpected status code on login: {login_response.status_code}"
    data = login_response.json()
    assert "access_token" in data, "access_token not in login response"
    assert data["token_type"] == "bearer", "Incorrect token_type in login response"

def test_login_non_existing_user(db_session: Session):
    """
    Test logging in with credentials that don't correspond to any user.
    """
    login_data = {"username": "nonexistentuser", "email": "nonexistent@example.com", "password": "password123"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
    data = response.json()
    assert data["detail"] == "User not found", "Incorrect error detail for non-existing user login"

def test_login_wrong_password(db_session: Session):
    """
    Test logging in with correct username and email but wrong password.
    """
    # First, create a user via /users/signup
    user_data = {"username": "testloginuser2", "email": "testlogin2@example.com", "password": "password123"}
    signup_response = client.post("/users/signup", json=user_data)
    assert signup_response.status_code == 200, f"Unexpected status code on signup: {signup_response.status_code}"
    
    # Attempt to login with wrong password
    login_data = {"username": "testloginuser2", "email": "testlogin2@example.com", "password": "wrongpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 404, f"Expected 404 Not Found for wrong password, got {login_response.status_code}"
    data = login_response.json()
    assert data["detail"] == "User not found", "Incorrect error detail for wrong password login"

@pytest.mark.parametrize(
    "login_data",
    [
        # Missing username
        {"email": "test1@example.com", "password": "password123"},
        # Missing email
        {"username": "user1", "password": "password123"},
        # Missing password
        {"username": "user1", "email": "test2@example.com"},
        # Invalid email format
        {"username": "user2", "email": "invalidemail", "password": "password123"},
        # Short password
        {"username": "user3", "email": "test3@example.com", "password": "short"},
    ]
)
def test_login_invalid_input(db_session: Session, login_data):
    """
    Test logging in with invalid input data.
    """
    response = client.post(
        "/auth/login",
        json=login_data
    )
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Error details missing in response"

def test_login_existing_user_multiple_times(db_session: Session):
    """
    Test logging in multiple times with the same user to ensure consistent behavior.
    """
    # First, create a user via /users/signup
    user_data = {"username": "testloginuser3", "email": "testlogin3@example.com", "password": "password123"}
    signup_response = client.post("/users/signup", json=user_data)
    assert signup_response.status_code == 200, f"Unexpected status code on signup: {signup_response.status_code}"
    
    # Attempt to login multiple times
    login_data = {"username": "testloginuser3", "email": "testlogin3@example.com", "password": "password123"}
    for i in range(5):
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Unexpected status code on login attempt {i+1}: {login_response.status_code}"
        data = login_response.json()
        assert "access_token" in data, f"access_token missing on login attempt {i+1}"
        assert data["token_type"] == "bearer", f"Incorrect token_type on login attempt {i+1}"

def test_login_case_insensitive_email(db_session: Session):
    """
    Test that email login is case-sensitive or case-insensitive based on implementation.
    Assuming emails are case-sensitive.
    """
    # First, create a user via /users/signup
    user_data = {"username": "testloginuser4", "email": "testlogin4@example.com", "password": "password123"}
    signup_response = client.post("/users/signup", json=user_data)
    assert signup_response.status_code == 200, f"Unexpected status code on signup: {signup_response.status_code}"
    
    # Attempt to login with different case in email
    login_data = {"username": "testloginuser4", "email": "TestLogin4@Example.com", "password": "password123"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 404, f"Expected 404 Not Found for case-mismatched email, got {login_response.status_code}"
    data = login_response.json()
    assert data["detail"] == "User not found", "Incorrect error detail for case-mismatched email login"