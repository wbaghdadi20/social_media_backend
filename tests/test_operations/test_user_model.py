# import pytest
# from sqlalchemy.orm import Session
# import app.models as models
# from app.schemas import UserCreate, UserPrivate
# import app.services.user_service as user_service
# import app.crud.user_crud as user_crud
# from ..conftest import engine, TestingSessionLocal

# @pytest.fixture
# def session():
#     models.Base.metadata.create_all(bind=engine)
#     db = TestingSessionLocal()

#     # create test user in db
#     test_user = models.User(
#         username="testuser",
#         email="testuser@example.com",
#         password=user_service.get_hashed_password("password123")
#     )
#     db.add(test_user)
#     db.commit()

#     yield db

#     db.close()
#     models.Base.metadata.drop_all(bind=engine)

import pytest
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserPrivate
import app.services.user_service as user_service
import app.crud.user_crud as user_crud

def test_create_user(db_session: Session):
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

# ------------------------
# --- Additional Tests ---
# ------------------------


# def test_unique_username(db_session):
#     """
#     Test that usernames must be unique.
#     """
#     create_user(db_session, 'uniqueuser', 'user1@example.com', 'password1')
#     with pytest.raises(IntegrityError):
#         create_user(db_session, 'uniqueuser', 'user2@example.com', 'password2')


# def test_unique_email(db_session):
#     """
#     Test that emails must be unique.
#     """
#     create_user(db_session, 'user1', 'uniqueemail@example.com', 'password1')
#     with pytest.raises(IntegrityError):
#         create_user(db_session, 'user2', 'uniqueemail@example.com', 'password2')


# def test_invalid_username(db_session):
#     """
#     Test creating a user with invalid username.
#     """
#     with pytest.raises(IntegrityError):
#         create_user(db_session, username=None, email='valid@example.com', password='password123')


# def test_invalid_email(db_session):
#     """
#     Test creating a user with invalid email.
#     """
#     with pytest.raises(IntegrityError):
#         create_user(db_session, username='validuser', email=None, password='password123')


# def test_invalid_password(db_session):
#     """
#     Test creating a user with invalid password.
#     """
#     with pytest.raises(TypeError):
#         create_user(db_session, username='validuser', email='valid@example.com', password=None)