import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import Token, UserPrivate, UserCreate
from fastapi.testclient import TestClient

def test_login_valid_user(
    client: TestClient, 
    db_session: Session,
    existing_user: UserPrivate
):
    user_create_data = {"username": "test_user", "email": "test_user@example.com", "password": "password123"}
    response = client.post(
        "/auth/login",
        json=user_create_data
    )
    assert response.status_code == 200
    
    token = Token(**response.json())
    assert token.access_token is not None
    assert token.token_type == "bearer"


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": "nonexistentuser", "email": "uniqueuser@example.com", "password": "password123"}, # wrong username
        {"username": "uniqueuser", "email": "nonexistentuser@example.com", "password": "password123"}, # wrong email
        {"username": "uniqueuser", "email": "uniqueuser@example.com", "password": "wrongpassword"}, # wrong password
    ]
)
def test_login_non_existing_user(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Parametrized test for logging in with incorrect username, email, or password.
    """
    response = client.post(
        "/auth/login",
        json=user_create_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": None, "email": "uniqueuser@example.com", "password": "password123"},  # None
        {"username": "A", "email": "uniqueuser@example.com", "password": "password123"},  # too short
        {"username": "A" * 51, "email": "uniqueuser@example.com", "password": "password123"},  # too long
    ]
)
def test_login_invalid_username(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Test logging in with invalid username.
    """
    response = client.post(
        "/auth/login",
        json=user_create_data
    )
    assert response.status_code == 422


def test_login_invalid_email(client: TestClient, db_session: Session):
    """
    Test logging in with invalid email.
    """
    user_create_data = {"username": "uniqueuser", "email": None, "password": "password123"}
    response = client.post(
        "/auth/login",
        json=user_create_data
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": "uniqueuser", "email": "uniqueuser@example.com", "password": None},  # None
        {"username": "uniqueuser", "email": "uniqueuser@example.com", "password": "A" * 7},  # too short
    ]
)
def test_login_invalid_password(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Test logging in with invalid password.
    """
    response = client.post(
        "/auth/login",
        json=user_create_data
    )
    assert response.status_code == 422


def test_login_valid_user_multiple_times(
    client: TestClient, 
    db_session: Session,
    existing_user: UserPrivate
):
    user_create_data = {"username": "test_user", "email": "test_user@example.com", "password": "password123"}
    for i in range(5):
        response = client.post(
            "/auth/login",
            json=user_create_data
        )
        assert response.status_code == 200
        token = Token(**response.json())
        assert token.access_token is not None
        assert token.token_type == "bearer"