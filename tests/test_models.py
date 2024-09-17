import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models import User, Post, Comment, PostLike, CommentLike, Follow
from app.config.database import Base
import uuid

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope='session')
def engine():
    """
    Creates a new SQLAlchemy engine for the testing session.
    Uses an in-memory SQLite database.
    """
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope='session')
def BaseModel():
    """
    Provides the declarative base model for the session.
    """
    return Base


@pytest.fixture(scope='function')
def db_session(engine, BaseModel):
    """
    Creates a new database session for a test and ensures a clean state.
    - Creates all tables before the test.
    - Drops all tables after the test.
    - Enables foreign key constraints in SQLite.
    """
    # Create all tables
    BaseModel.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Enable foreign key constraints for SQLite
    session.execute(text('PRAGMA foreign_keys=ON'))

    yield session  # This is where the testing happens

    session.rollback()  # Rollback any changes made during the test
    session.close()
    # Drop all tables
    BaseModel.metadata.drop_all(engine)


# Helper functions to reduce code duplication
def create_user(db_session, username, email, password_hash='hashedpassword'):
    """
    Helper function to create and commit a user to the database.
    
    :param db_session: SQLAlchemy session object
    :param username: Username of the user
    :param email: Email of the user
    :param password_hash: Hashed password of the user
    :return: The created User object
    """
    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db_session.add(user)
    db_session.commit()
    return user


def create_post(db_session, owner_id, content='Test content', caption='Test caption'):
    """
    Helper function to create and commit a post to the database.
    
    :param db_session: SQLAlchemy session object
    :param owner_id: UUID of the user who owns the post
    :param content: Content of the post
    :param caption: Caption of the post
    :return: The created Post object
    """
    post = Post(
        owner_id=owner_id,
        content=content,
        caption=caption
    )
    db_session.add(post)
    db_session.commit()
    return post


def create_comment(db_session, post_id, user_id, content='Test comment'):
    """
    Helper function to create and commit a comment to the database.
    
    :param db_session: SQLAlchemy session object
    :param post_id: UUID of the post being commented on
    :param user_id: UUID of the user making the comment
    :param content: Content of the comment
    :return: The created Comment object
    """
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content
    )
    db_session.add(comment)
    db_session.commit()
    return comment


def create_post_like(db_session, user_id, post_id):
    """
    Helper function to create and commit a post like to the database.
    
    :param db_session: SQLAlchemy session object
    :param user_id: UUID of the user liking the post
    :param post_id: UUID of the post being liked
    :return: The created PostLike object
    """
    post_like = PostLike(
        user_id=user_id,
        post_id=post_id
    )
    db_session.add(post_like)
    db_session.commit()
    return post_like


def create_comment_like(db_session, user_id, comment_id):
    """
    Helper function to create and commit a comment like to the database.
    
    :param db_session: SQLAlchemy session object
    :param user_id: UUID of the user liking the comment
    :param comment_id: UUID of the comment being liked
    :return: The created CommentLike object
    """
    comment_like = CommentLike(
        user_id=user_id,
        comment_id=comment_id
    )
    db_session.add(comment_like)
    db_session.commit()
    return comment_like


def create_follow(db_session, follower_id, followed_id):
    """
    Helper function to create and commit a follow relationship to the database.
    
    :param db_session: SQLAlchemy session object
    :param follower_id: UUID of the follower
    :param followed_id: UUID of the user being followed
    :return: The created Follow object
    """
    follow = Follow(
        follower_id=follower_id,
        followed_id=followed_id
    )
    db_session.add(follow)
    db_session.commit()
    return follow


# -------------------------------
# User Model Tests
# -------------------------------

def test_create_user(db_session):
    """
    Test creating a valid user.
    """
    user = create_user(db_session, 'testuser', 'testuser@example.com')
    retrieved_user = db_session.query(User).filter_by(username='testuser').first()
    assert retrieved_user is not None
    assert retrieved_user.email == 'testuser@example.com'


def test_unique_username(db_session):
    """
    Test that usernames must be unique.
    """
    create_user(db_session, 'uniqueuser', 'user1@example.com')
    with pytest.raises(IntegrityError):
        create_user(db_session, 'uniqueuser', 'user2@example.com')


def test_unique_email(db_session):
    """
    Test that emails must be unique.
    """
    create_user(db_session, 'user1', 'uniqueemail@example.com')
    with pytest.raises(IntegrityError):
        create_user(db_session, 'user2', 'uniqueemail@example.com')


@pytest.mark.parametrize("username", [
    '',         # Empty string
    'ab',       # Too short (< 3)
    'u' * 51,   # Too long (> 50)
    None        # None value
])
def test_invalid_username(db_session, username):
    """
    Test creating a user with invalid usernames.
    """
    with pytest.raises(IntegrityError):
        create_user(db_session, username=username, email='valid@example.com')


@pytest.mark.parametrize("email", [
    '',                     # Empty string
    'invalidemail',         # Missing '@' and domain
    'user@',                # Missing domain
    'user@example',         # Missing top-level domain
    None                    # None value
])
def test_invalid_email(db_session, email):
    """
    Test creating a user with invalid emails.
    """
    with pytest.raises(IntegrityError):
        create_user(db_session, username='validuser', email=email)


@pytest.mark.parametrize("password_hash", [
    '',             # Empty string
    'short',        # Too short (< 8)
    ' ' * 7,        # Only spaces, length < 8
    None            # None value
])
def test_invalid_password_hash(db_session, password_hash):
    """
    Test creating a user with invalid password hashes.
    """
    with pytest.raises(IntegrityError):
        create_user(db_session, username='validuser', email='valid@example.com', password_hash=password_hash)


# -------------------------------
# Follow Model Tests
# -------------------------------

def test_user_following(db_session):
    """
    Test creating a follow relationship between two users.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
    assert user1.following[0].followed == user2
    assert user2.followers[0].follower == user1


def test_unique_follow(db_session):
    """
    Test that a user cannot follow the same user more than once.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=user1.id, followed_id=user2.id)


def test_user_following_nonexistent_user(db_session):
    """
    Test that following a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=user.id, followed_id=non_existent_user_id)


def test_user_followed_by_nonexistent_user(db_session):
    """
    Test that a non-existent user cannot follow a user.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=non_existent_user_id, followed_id=user.id)


def test_user_cannot_follow_themselves(db_session):
    """
    Test that a user cannot follow themselves.
    """
    user = create_user(db_session, 'selfuser', 'selfuser@example.com')
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=user.id, followed_id=user.id)


def test_follow_nonexistent_user(db_session):
    """
    Test that following a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=user.id, followed_id=non_existent_user_id)


def test_nonexistent_user_follows_user(db_session):
    """
    Test that a non-existent user cannot follow a user.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=non_existent_user_id, followed_id=user.id)


def test_delete_user_deletes_follows(db_session):
    """
    Test that deleting a user deletes associated follow relationships.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
    db_session.delete(user1)
    db_session.commit()
    # The follow relationship should be deleted due to cascade
    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).first()
    assert follow is None


# -------------------------------
# Post Model Tests
# -------------------------------

def test_create_post(db_session):
    """
    Test creating a valid post.
    """
    user = create_user(db_session, 'postuser', 'postuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    retrieved_post = db_session.query(Post).filter_by(id=post.id).first()
    assert retrieved_post is not None
    assert retrieved_post.content == 'Test content'
    assert retrieved_post.caption == 'Test caption'


def test_create_post_with_null_owner(db_session):
    """
    Test that creating a post without an owner fails.
    """
    with pytest.raises(IntegrityError):
        create_post(db_session, owner_id=None)


def test_create_post_with_empty_content(db_session):
    """
    Test that creating a post with empty content fails.
    """
    user = create_user(db_session, 'emptycontentuser', 'emptycontent@example.com')
    with pytest.raises(IntegrityError):
        create_post(db_session, owner_id=user.id, content='')


def test_create_post_with_long_caption(db_session):
    """
    Test that creating a post with a caption that's too long fails.
    """
    user = create_user(db_session, 'longcaptionuser', 'longcaption@example.com')
    long_caption = 'c' * 256  # Exceeds the 255 character limit
    with pytest.raises(IntegrityError):
        create_post(db_session, owner_id=user.id, caption=long_caption)


def test_post_owner_relationship(db_session):
    """
    Test that a post is linked to its owner correctly.
    """
    user = create_user(db_session, 'owneruser', 'owneruser@example.com')
    post = create_post(db_session, owner_id=user.id)
    assert post.owner == user
    assert user.posts[0] == post


def test_cascade_delete_post_comments(db_session):
    """
    Test that deleting a post also deletes its comments due to cascade.
    """
    user = create_user(db_session, 'cascadecommentuser', 'cascadecomment@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    db_session.delete(post)
    db_session.commit()
    # The comment should be deleted due to cascade
    deleted_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert deleted_comment is None


def test_delete_post_deletes_likes(db_session):
    """
    Test that deleting a post also deletes its likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    db_session.delete(post)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(PostLike).filter_by(id=like.id).first()
    assert deleted_like is None


# -------------------------------
# Comment Model Tests
# -------------------------------

def test_create_comment(db_session):
    """
    Test creating a valid comment on a post.
    """
    user = create_user(db_session, 'commentuser', 'commentuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    retrieved_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert retrieved_comment is not None
    assert retrieved_comment.content == 'Test comment'
    assert retrieved_comment.post == post
    assert retrieved_comment.owner == user


def test_create_comment_with_empty_content(db_session):
    """
    Test that creating a comment with empty content fails.
    """
    user = create_user(db_session, 'emptycommentuser', 'emptycomment@example.com')
    post = create_post(db_session, owner_id=user.id)
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=post.id, user_id=user.id, content='')


def test_create_comment_with_null_user(db_session):
    """
    Test that creating a comment without a user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    post = create_post(db_session, owner_id=user.id)
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=post.id, user_id=None)


def test_create_comment_with_null_post(db_session):
    """
    Test that creating a comment without a post fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=None, user_id=user.id)


def test_comment_owner_relationship(db_session):
    """
    Test that a comment is linked to its owner and post correctly.
    """
    user = create_user(db_session, 'commentowner', 'commentowner@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    assert comment.owner == user
    assert comment.post == post


def test_cascade_delete_user_comments(db_session):
    """
    Test that deleting a user also deletes their comments due to cascade.
    """
    user = create_user(db_session, 'commentuser', 'commentuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    db_session.delete(user)
    db_session.commit()
    # The comment should be deleted due to cascade
    deleted_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert deleted_comment is None


def test_comment_on_nonexistent_post(db_session):
    """
    Test that commenting on a non-existent post fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_post_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=non_existent_post_id, user_id=user.id)


# -------------------------------
# PostLike Model Tests
# -------------------------------

def test_post_like(db_session):
    """
    Test liking a valid post.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    post_like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    retrieved_like = db_session.query(PostLike).filter_by(id=post_like.id).first()
    assert retrieved_like is not None
    assert retrieved_like.user == user2
    assert retrieved_like.post == post


def test_unique_post_like(db_session):
    """
    Test that a user cannot like the same post more than once.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    post = create_post(db_session, owner_id=user.id)
    create_post_like(db_session, user_id=user.id, post_id=post.id)
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=user.id, post_id=post.id)


def test_create_post_like_with_nonexistent_user(db_session):
    """
    Test that liking a post with a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    post = create_post(db_session, owner_id=user.id)
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=non_existent_user_id, post_id=post.id)


def test_create_post_like_with_nonexistent_post(db_session):
    """
    Test that liking a non-existent post fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_post_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=user.id, post_id=non_existent_post_id)


def test_duplicate_post_like(db_session):
    """
    Test that a user cannot like the same post more than once.
    """
    user = create_user(db_session, 'likeuser', 'likeuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    create_post_like(db_session, user_id=user.id, post_id=post.id)
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=user.id, post_id=post.id)


def test_delete_post_deletes_likes(db_session):
    """
    Test that deleting a post also deletes its likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    db_session.delete(post)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(PostLike).filter_by(id=like.id).first()
    assert deleted_like is None


# -------------------------------
# CommentLike Model Tests
# -------------------------------

def test_comment_like(db_session):
    """
    Test liking a valid comment.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id)
    comment_like = create_comment_like(db_session, user_id=user1.id, comment_id=comment.id)
    retrieved_like = db_session.query(CommentLike).filter_by(id=comment_like.id).first()
    assert retrieved_like is not None
    assert retrieved_like.user == user1
    assert retrieved_like.comment == comment


def test_unique_comment_like(db_session):
    """
    Test that a user cannot like the same comment more than once.
    """
    user = create_user(db_session, 'likeuser', 'likeuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    create_comment_like(db_session, user_id=user.id, comment_id=comment.id)
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=user.id, comment_id=comment.id)


def test_create_comment_like_with_nonexistent_user(db_session):
    """
    Test that liking a comment with a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    non_existent_user_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=non_existent_user_id, comment_id=comment.id)


def test_create_comment_like_with_nonexistent_comment(db_session):
    """
    Test that liking a non-existent comment fails.
    """
    user = create_user(db_session, 'user', 'user@example.com')
    non_existent_comment_id = str(uuid.uuid4())
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=user.id, comment_id=non_existent_comment_id)


def test_duplicate_comment_like(db_session):
    """
    Test that a user cannot like the same comment more than once.
    """
    user = create_user(db_session, 'likeuser', 'likeuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    create_comment_like(db_session, user_id=user.id, comment_id=comment.id)
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=user.id, comment_id=comment.id)


def test_delete_comment_deletes_likes(db_session):
    """
    Test that deleting a comment also deletes its likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id)
    like = create_comment_like(db_session, user_id=user1.id, comment_id=comment.id)
    db_session.delete(comment)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(CommentLike).filter_by(id=like.id).first()
    assert deleted_like is None


# -------------------------------
# Additional Comprehensive Tests
# -------------------------------

def test_create_user_with_duplicate_email(db_session):
    """
    Test that creating users with duplicate emails fails.
    """
    create_user(db_session, 'user1', 'duplicate@example.com')
    with pytest.raises(IntegrityError):
        create_user(db_session, 'user2', 'duplicate@example.com')


def test_post_owner_relationship(db_session):
    """
    Test that a post is linked to its owner correctly.
    """
    user = create_user(db_session, 'owneruser', 'owneruser@example.com')
    post = create_post(db_session, owner_id=user.id)
    assert post.owner == user
    assert user.posts[0] == post


def test_delete_user_deletes_comments(db_session):
    """
    Test that deleting a user also deletes their comments due to cascade.
    """
    user = create_user(db_session, 'commentuser', 'commentuser@example.com')
    post = create_post(db_session, owner_id=user.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user.id)
    db_session.delete(user)
    db_session.commit()
    # The comment should be deleted due to cascade
    deleted_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert deleted_comment is None


def test_delete_user_deletes_post_likes(db_session):
    """
    Test that deleting a user also deletes their post likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    db_session.delete(user2)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(PostLike).filter_by(id=like.id).first()
    assert deleted_like is None


def test_delete_user_deletes_comment_likes(db_session):
    """
    Test that deleting a user also deletes their comment likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com')
    user2 = create_user(db_session, 'user2', 'user2@example.com')
    post = create_post(db_session, owner_id=user1.id)
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id)
    like = create_comment_like(db_session, user_id=user2.id, comment_id=comment.id)
    db_session.delete(user2)
    db_session.commit()
    # The comment like should be deleted due to cascade
    deleted_like = db_session.query(CommentLike).filter_by(id=like.id).first()
    assert deleted_like is None
