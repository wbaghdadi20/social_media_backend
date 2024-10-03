import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserPrivate, FollowBase, Token
from fastapi.testclient import TestClient
from freezegun import freeze_time
from datetime import datetime, timezone, timedelta
from app.config.config import ACCESS_TOKEN_EXPIRE_MINUTES

@pytest.fixture
def existing_user(client: TestClient, db_session: Session) -> User:
    """
    Fixture to pre-populate the db with a user
    """
    _ = client.post(
        "/auth/signup",
        json={"username": "test_user", "email": "test_user@example.com", "password": "password123"}
    )
    return db_session.query(User).filter_by(email="test_user@example.com").first()

@pytest.fixture
def unique_user(client: TestClient, db_session: Session) -> User:
    """
    Fixture to pre-populate the db with a user
    """
    _ = client.post(
        "/auth/signup",
        json={"username": "unique_user", "email": "unique_user@example.com", "password": "password123"}
    )
    return db_session.query(User).filter_by(email="unique_user@example.com").first()

@pytest.fixture
def authenticated_user_token(client: TestClient, db_session: Session) -> Token:
    response = client.post(
        "/auth/signup",
        json={"username": "authenticated_user", "email": "authenticated_user@example.com", "password": "password123"}
    )
    token_data = Token(**response.json())
    return token_data.access_token

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
    assert user_prvt.username == "authenticated_user"
    assert user_prvt.email == "authenticated_user@example.com"
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
    assert user_prvt.username == "authenticated_user"
    assert user_prvt.email == "authenticated_user@example.com"
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
    assert user_prvt.username == "authenticated_user"
    assert user_prvt.email == "authenticated_user@example.com"
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


def test_valid_delete(
    client: TestClient,
    db_session: Session,
    authenticated_user_token: str
):
    response = client.delete(
        "/users/delete",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "authenticated_user successfully deleted"

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_delete_invalid_token(client: TestClient, db_session: Session):
    invalid_token = "randomInvalidToken123"
    response = client.delete(
        "/users/delete",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
    

def test_delete_deleted_user(
    client: TestClient,
    db_session: Session,
    authenticated_user_token: str
):
    _ = client.delete(
        "/users/delete",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )

    response = client.delete(
        "/users/delete",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_valid_follow(
    client: TestClient,
    db_session: Session,
    existing_user: User,
    authenticated_user_token: str
):
    response = client.post(
        "users/follow?username_to_follow=test_user",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    follow = FollowBase(**response.json())
    assert response.status_code == 200
    assert follow.follower_id == db_session.query(User).filter(User.username == "authenticated_user").first().id
    assert follow.followed_id == db_session.query(User).filter(User.username == "test_user").first().id


@pytest.mark.parametrize(
    "username_to_follow, expected_status_code, expected_detail",
    [
        (
            "user_not_found", 
            404,
            "User not found" 
        ),
        (
            "test_user",
            403,
            "You are already following this user"
        ),
        (
            "authenticated_user",
            403,
            "User can't follow themselves"
        )
    ]
)
def test_invalid_follow(
    client: TestClient,
    db_session: Session,
    existing_user: User,
    username_to_follow: str,
    expected_status_code: int,
    expected_detail: str,
    authenticated_user_token: str
):
    _ = client.post(
        "users/follow?username_to_follow=test_user",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )

    response = client.post(
        f"users/follow?username_to_follow={username_to_follow}",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == expected_status_code
    assert response.json()["detail"] == expected_detail


def test_valid_unfollow(
    client: TestClient,
    db_session: Session,
    existing_user: User,
    authenticated_user_token: str
):
    _ = client.post(
        "users/follow?username_to_follow=test_user",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )

    response = client.delete(
        "users/unfollow?username_to_unfollow=test_user",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "authenticated_user successfully unfollowed test_user"}


@pytest.mark.parametrize(
    "username_to_unfollow, expected_status_code, expected_detail",
    [
        (
            "user_not_found", 
            404,
            "User not found" 
        ),
        (
            "unique_user",
            403,
            "User can't unfollow user they dont follow"
        ),
        (
            "authenticated_user",
            403,
            "User can't unfollow themselves"
        )
    ]
)
def test_invalid_unfollow(
    client: TestClient,
    db_session: Session,
    unique_user: User,
    existing_user: User,
    username_to_unfollow: str,
    expected_status_code: int,
    expected_detail: str,
    authenticated_user_token: str
):  
    _ = client.post(
        "users/follow?username_to_follow=test_user",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )

    response = client.delete(
        f"users/unfollow?username_to_unfollow={username_to_unfollow}",
        headers={"Authorization": f"Bearer {authenticated_user_token}"}
    )
    assert response.status_code == expected_status_code
    assert response.json()["detail"] == expected_detail