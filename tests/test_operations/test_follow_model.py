import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import IntegrityError
import uuid
from app.schemas import UserCreate, UserPrivate, FollowBase
from app.models import Follow, User
import app.services.auth_service as auth_service
import app.services.user_service as user_service

@pytest.fixture
def user1(db_session: Session) -> UserPrivate:
    """Fixture to create and return user1."""
    return auth_service.create_user(
        user_create=UserCreate(username="user1", email="user1@example.com", password="password123"),
        db=db_session
    )

@pytest.fixture
def user2(db_session: Session) -> UserPrivate:
    """Fixture to create and return user2."""
    return auth_service.create_user(
        user_create=UserCreate(username="user2", email="user2@example.com", password="password123"),
        db=db_session
    )

@pytest.fixture
def follow_relationship(db_session: Session, user1: UserPrivate, user2: UserPrivate) -> FollowBase:
    """Fixture to create a follow relationship where user1 follows user2."""
    return user_service.follow_user(current_user=user1, username_to_follow=user2.username, db=db_session)


def test_create_valid_follow(db_session: Session, user1: UserPrivate, user2: UserPrivate):
    """
    Test creating a valid follow relationship directly.
    """
    follow = Follow(follower_id=user1.id, followed_id=user2.id)
    db_session.add(follow)
    db_session.commit()

    follow_db = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).one()
    assert follow_db is not None
    assert follow_db.follower_id == user1.id
    assert follow_db.followed_id == user2.id


def test_follow_already_following(db_session: Session, user1: UserPrivate, user2: UserPrivate, follow_relationship: Follow):
    """
    Test that a user cannot follow another user twice.
    """
    duplicate_follow = Follow(follower_id=user1.id, followed_id=user2.id)

    with pytest.raises(IntegrityError):
        db_session.add(duplicate_follow)
        db_session.commit()


def test_unfollow_user(db_session: Session, user1: UserPrivate, user2: UserPrivate, follow_relationship: Follow):
    """
    Test unfollowing a user directly.
    """
    follow_db = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).one()
    db_session.delete(follow_db)
    db_session.commit()

    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).first()
    assert follow is None


def test_unfollow_not_following(db_session: Session, user1: UserPrivate, user2: UserPrivate):
    """
    Test unfollowing a user that is not being followed.
    """
    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).first()
    assert follow is None

    with pytest.raises(UnmappedInstanceError):
        db_session.delete(follow)
        db_session.commit()


def test_unfollow_self(db_session: Session, user1: UserPrivate):
    """
    Test that a user cannot unfollow themselves directly.
    """
    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user1.id).first()
    assert follow is None


def test_cascade_delete(db_session: Session, user1: UserPrivate, user2: UserPrivate, follow_relationship: Follow):
    """
    Test that when a user is deleted, their follow relationships are also deleted.
    """
    db_session.delete(db_session.query(User).filter(User.id == user1.id).first())
    db_session.commit()

    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).first()
    assert follow is None


def test_follow_invalid_follower_id(db_session: Session, user2: UserPrivate):
    """
    Test creating a follow relationship with an invalid follower_id.
    """
    with pytest.raises(IntegrityError):
        invalid_follower_id = uuid.uuid4()
        follow = Follow(follower_id=invalid_follower_id, followed_id=user2.id)
        db_session.add(follow)
        db_session.commit()


def test_follow_invalid_followed_id(db_session: Session, user1: UserPrivate):
    """
    Test creating a follow relationship with an invalid followed_id.
    """
    with pytest.raises(IntegrityError):
        invalid_followed_id = uuid.uuid4()
        follow = Follow(follower_id=user1.id, followed_id=invalid_followed_id)
        db_session.add(follow)
        db_session.commit()


def test_follow_unique_constraint(db_session: Session, user1: UserPrivate, user2: UserPrivate, follow_relationship: Follow):
    """
    Test that a follow relationship must be unique (combination of follower_id and followed_id).
    """
    with pytest.raises(IntegrityError):
        duplicate_follow = Follow(follower_id=user1.id, followed_id=user2.id)
        db_session.add(duplicate_follow)
        db_session.commit()
