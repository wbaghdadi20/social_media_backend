import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import Token, UserPrivate
from fastapi.testclient import TestClient
from freezegun import freeze_time
from datetime import datetime, timezone, timedelta
from app.config.config import ACCESS_TOKEN_EXPIRE_MINUTES

@pytest.fixture
def existing_user(client: TestClient, db_session: Session):
    """
    Fixture to pre-populate the db with a user
    """
    _ = client.post(
        "/users/signup",
        json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    return db_session.query(User).filter_by(email="testuser@example.com").first()

@pytest.fixture
def authenticated_user_token(client: TestClient, db_session: Session):
    signup_response = client.post(
        "/users/signup",
        json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    token_data = Token(**signup_response.json())
    return token_data.access_token


def test_signup_valid_user(client: TestClient, db_session: Session):
    response = client.post(
        "/users/signup",
        json={"username": "uniqueuser", "email": "uniqueuser@example.com", "password": "password123"}
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
            {"username": "testuser", "email": "uniqueuser@example.com", "password": "password123"},
            "Username is already registered"
        ),
        (
            {"username": "uniqueuser", "email": "testuser@example.com", "password": "password123"},
            "Email is already registered"
        ),
        (
            {"username": "testuser", "email": "testuser@example.com", "password": "password123"},
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
        "/users/signup",
        json=user_create_data
    )
    assert response.status_code == 409
    assert response.json()["detail"] == expected_detail


@pytest.mark.parametrize(
    "user_create_data",
    [
        {"username": None, "email": "uniqueuser@example.com", "password": "password123"},  # None       
        {"username": "A", "email": "uniqueuser@example.com", "password": "password123"},  # too short
        {"username": "A" * 51, "email": "uniqueuser@example.com", "password": "password123"},  # too long
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
        "/users/signup",
        json=user_create_data
    )
    assert response.status_code == 422  


def test_signup_invalid_email(client: TestClient, db_session: Session):
    """
    Test creating a user with invalid email.
    """
    user_create_data = {"username": "uniqueuser", "email": None, "password": "password123"}
    response = client.post(
        "/users/signup",
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
def test_signup_invalid_password(
    client: TestClient,
    db_session: Session,
    user_create_data: dict
):
    """
    Test creating a user with invalid password.
    """
    response = client.post(
        "/users/signup",
        json=user_create_data
    )
    assert response.status_code == 422 


def test_me_valid_token(
    client: TestClient,
    db_session: Session,
    authenticated_user_token: str
):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 200

    user_prvt = UserPrivate(**response.json())
    assert user_prvt.username == "testuser"
    assert user_prvt.email == "testuser@example.com"
    assert user_prvt.created_at is not None
    assert user_prvt.id is not None


def test_me_expired_token(
    client: TestClient,
    db_session: Session,
    authenticated_user_token: str
):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 200
    
    user_prvt = UserPrivate(**response.json())
    assert user_prvt.username == "testuser"
    assert user_prvt.email == "testuser@example.com"
    assert user_prvt.created_at is not None
    assert user_prvt.id is not None

    with freeze_time(
        datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    ):
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {authenticated_user_token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Token has expired"

def test_me_no_token(client: TestClient, db_session: Session):
    response = client.get("/users/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_me_invalid_token(client: TestClient, db_session: Session):
    invalid_token = "randomInvalidToken123"
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_me_deleted_user(
    client: TestClient,
    db_session: Session,
    authenticated_user_token: str
):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 200
    user_prvt = UserPrivate(**response.json())
    assert user_prvt.username == "testuser"
    assert user_prvt.email == "testuser@example.com"
    assert user_prvt.created_at is not None
    assert user_prvt.id is not None

    user_db = db_session.query(User).filter(User.username == user_prvt.username).first()
    db_session.delete(user_db)
    db_session.commit()

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"