import pytest
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.schemas import UserCreate, UserPrivate, EmailAlreadyRegistered, UsernameAlreadyRegistered
import app.services.user_service as user_service
import app.crud.user_crud as user_crud

def test_create_valid_user(db_session: Session):
    """
    Test creating a valid user.
    """
    user_create = UserCreate(
        username="uniqueuser",
        email="uniqueuser@example.com",
        password="password123"
    )
    user = user_service.create_user(
        user_create=user_create,
        db=db_session
    )
    user_db = user_crud.get_user_by_login(login_data=user_create, db=db_session)
    user_db_private = UserPrivate.model_validate(user_db, strict=True)
    assert user == user_db_private


@pytest.mark.parametrize(
    "user_create, expected_exception, expected_message",
    [
        (
            UserCreate(
                username="testuser",
                email="uniqueuser@example.com",
                password="password123"
            ),
            UsernameAlreadyRegistered,
            "Username is already registered"            
        ),
        (
            UserCreate(
                username="uniqueuser",
                email="testuser@example.com",
                password="password123"
            ),
            EmailAlreadyRegistered,
            "Email is already registered"            
        ),
        (
            UserCreate(
                username="testuser",
                email="testuser@example.com",
                password="password123"
            ), 
            EmailAlreadyRegistered,
            "Email is already registered"            
        )
    ]
)
def test_create_duplicate_user(
    db_session: Session,
    existing_user: UserPrivate,
    user_create: UserCreate,
    expected_exception,
    expected_message
):
    """
    Test that user must be unique (username/email).
    """
    with pytest.raises(expected_exception) as exc_info:
        user_service.create_user(user_create=user_create, db=db_session)

    exception = exc_info.value
    assert exception.message == expected_message


@pytest.mark.parametrize(
    "user_create_data, expected_exception, expected_message",
    [
        (
            {"username": None, "email": "uniqueuser@example.com", "password": "password123"},  # None
            ValidationError,
            "Input should be a valid string"
        ),
        (
            {"username": "A", "email": "uniqueuser@example.com", "password": "password123"},  # too short
            ValidationError,
            "String should have at least 3 characters"
        ),
        (
            {"username": "A" * 51, "email": "uniqueuser@example.com", "password": "password123"},  # too long
            ValidationError,
            "String should have at most 50 characters"
        )
    ]
)
def test_invalid_username(
    db_session: Session,
    user_create_data: dict,
    expected_exception,
    expected_message
):
    """
    Test creating a user with invalid username.
    """
    with pytest.raises(expected_exception) as exc_info:
        user_create = UserCreate(**user_create_data)
        user_service.create_user(user_create=user_create, db=db_session)

    assert expected_message == exc_info.value.errors()[0]["msg"]    


# Wont test for all types of bad formatting
def test_invalid_email(db_session: Session):
    """
    Test creating a user with invalid email (None).
    """
    user_create_data = {"username": "uniqueuser", "email": None, "password": "password123"}  # None
    expected_exception = ValidationError
    expected_message = "Input should be a valid string"
    
    with pytest.raises(expected_exception) as exc_info:
        user_create = UserCreate(**user_create_data)
        user_service.create_user(user_create=user_create, db=db_session)

    assert expected_message == exc_info.value.errors()[0]["msg"]


@pytest.mark.parametrize(
    "user_create_data, expected_exception, expected_message",
    [
        (
            {"username": "uniqueuser", "email": "user@example.com", "password": None},  # None
            ValidationError,
            "Input should be a valid string"
        ),
        (
            {"username": "uniqueuser", "email": "user@example.com", "password": "A" * 7},  # too short
            ValidationError,
            "String should have at least 8 characters"
        )
    ]
)
def test_invalid_password(
    db_session: Session,
    user_create_data: dict,
    expected_exception,
    expected_message: str
):
    """
    Test creating a user with invalid password.
    """
    with pytest.raises(expected_exception) as exc_info:
        user_create = UserCreate(**user_create_data)
        user_service.create_user(user_create=user_create, db=db_session)

    assert expected_message == exc_info.value.errors()[0]["msg"]