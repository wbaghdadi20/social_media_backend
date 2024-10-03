import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import Token, UserPrivate, UserCreate
from fastapi.testclient import TestClient

def test_signup_valid_user(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/signup",
        json={"username": "unique_user", "email": "unique_user@example.com", "password": "password123"}
    )
    assert response.status_code == 200

    token = Token(**response.json())
    assert token.access_token is not None
    assert token.token_type == "bearer"


# might be a dup test?
@pytest.mark.parametrize(
    "user_create_data, expected_detail",
    [
        (
            {"username": "test_user", "email": "unique_user@example.com", "password": "password123"},
            "Username is already registered"
        ),
        (
            {"username": "unique_user", "email": "test_user@example.com", "password": "password123"},
            "Email is already registered"
        ),
        (
            {"username": "test_user", "email": "test_user@example.com", "password": "password123"},
            "Email is already registered"
        )
    ]
)
def test_signup_duplicate_user(
    client: TestClient,
    existing_user: User,
    user_create_data: dict,
    expected_detail
):
    """
    Test that creating a user with a duplicate username/email returns the correct HTTP response.
    """ 
    response = client.post(
        "/auth/signup",
        json=user_create_data
    )
    assert response.status_code == 409
    assert response.json()["detail"] == expected_detail


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": None, "email": "unique_user@example.com", "password": "password123"},  # None       
        {"username": "A", "email": "unique_user@example.com", "password": "password123"},  # too short
        {"username": "A" * 51, "email": "unique_user@example.com", "password": "password123"},  # too long
    ]
)
def test_signup_invalid_username(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Test creating a user with invalid username.
    """
    response = client.post(
        "/auth/signup",
        json=user_create_data
    )
    assert response.status_code == 422  


def test_signup_invalid_email(client: TestClient, db_session: Session):
    """
    Test creating a user with invalid email.
    """
    user_create_data = {"username": "unique_user", "email": None, "password": "password123"}
    response = client.post(
        "/auth/signup",
        json=user_create_data
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": "unique_user", "email": "unique_user@example.com", "password": None},  # None
        {"username": "unique_user", "email": "unique_user@example.com", "password": "A" * 7},  # too short
    ]
)
def test_signup_invalid_password(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Test creating a user with invalid password.
    """
    response = client.post(
        "/auth/signup",
        json=user_create_data
    )
    assert response.status_code == 422 

  
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