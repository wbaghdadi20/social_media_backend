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
def create_user(db_session, username, email, password):
    """
    Helper function to create and commit a user to the database.
    
    :param db_session: SQLAlchemy session object
    :param username: Username of the user
    :param email: Email of the user
    :param password: Plain password of the user
    :return: The created User object
    """
    user = User(
        username=username,
        email=email,
        password="hashed" + password
    )
    db_session.add(user)
    db_session.commit()
    return user


def create_post(db_session, owner_id, content, caption):
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


def create_comment(db_session, post_id, user_id, content):
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
    user = create_user(db_session, 'testuser', 'testuser@example.com', 'password123')
    retrieved_user = db_session.query(User).filter_by(username=user.username).first()
    assert retrieved_user == user

def test_unique_username(db_session):
    """
    Test that usernames must be unique.
    """
    create_user(db_session, 'uniqueuser', 'user1@example.com', 'password1')
    with pytest.raises(IntegrityError):
        create_user(db_session, 'uniqueuser', 'user2@example.com', 'password2')


def test_unique_email(db_session):
    """
    Test that emails must be unique.
    """
    create_user(db_session, 'user1', 'uniqueemail@example.com', 'password1')
    with pytest.raises(IntegrityError):
        create_user(db_session, 'user2', 'uniqueemail@example.com', 'password2')


def test_invalid_username(db_session):
    """
    Test creating a user with invalid username.
    """
    with pytest.raises(IntegrityError):
        create_user(db_session, username=None, email='valid@example.com', password='password123')


def test_invalid_email(db_session):
    """
    Test creating a user with invalid email.
    """
    with pytest.raises(IntegrityError):
        create_user(db_session, username='validuser', email=None, password='password123')


def test_invalid_password(db_session):
    """
    Test creating a user with invalid password.
    """
    with pytest.raises(TypeError):
        create_user(db_session, username='validuser', email='valid@example.com', password=None)


def test_delete_user_deletes_follows(db_session):
    """
    Test that deleting a user deletes associated follow relationships.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')
    create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
    db_session.delete(user1)
    db_session.commit()
    # The follow relationship should be deleted due to cascade
    follow = db_session.query(Follow).filter_by(follower_id=user1.id, followed_id=user2.id).first()
    assert follow is None


def test_delete_user_deletes_posts(db_session):
    """
    Test that deleting a user deletes their posts.
    """
    user = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    post = create_post(db_session, owner_id=user.id, content='Post for deleting user post', caption='Delete User Posts Test')
    db_session.delete(user)
    db_session.commit()
    # The post should be deleted due to cascade
    deleted_post = db_session.query(Post).filter_by(id=post.id).first()
    assert deleted_post is None


def test_delete_user_deletes_post_likes(db_session):
    """
    Test that deleting a user also deletes their post likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')
    post = create_post(db_session, owner_id=user1.id, content='Post for deleting user likes', caption='Delete User Likes Test')
    like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    db_session.delete(user2)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(PostLike).filter_by(id=like.id).first()
    assert deleted_like is None


def test_delete_user_deletes_comments(db_session):
    """
    Test that deleting a user also deletes their comments due to cascade.
    """
    user = create_user(db_session, 'commentuser', 'commentuser@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for deleting comments', caption='Cascade Delete Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='This comment will be deleted.')
    db_session.delete(user)
    db_session.commit()
    # The comment should be deleted due to cascade
    deleted_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert deleted_comment is None


def test_delete_user_deletes_comment_likes(db_session):
    """
    Test that deleting a user also deletes their comment likes due to cascade.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')
    post = create_post(db_session, owner_id=user1.id, content='Post for deleting comment likes', caption='Delete Comment Likes Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id, content='Comment for deleting likes')
    like = create_comment_like(db_session, user_id=user2.id, comment_id=comment.id)
    db_session.delete(user2)
    db_session.commit()
    # The comment like should be deleted due to cascade
    deleted_like = db_session.query(CommentLike).filter_by(id=like.id).first()
    assert deleted_like is None


# -------------------------------
# Follow Model Tests
# -------------------------------

def test_user_following(db_session):
    """
    Test creating a follow relationship between two users.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')
    follow = create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
    assert follow.follower == user1
    assert follow.followed == user2
    assert user1.following[0] == follow
    assert user2.followers[0] == follow


# def test_unique_follow(db_session):
#     """
#     Test that a user cannot follow the same user more than once.
#     """
#     user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
#     user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')
#     create_follow(db_session, follower_id=user1.id, followed_id=user2.id)
#     with pytest.raises(IntegrityError):
#         create_follow(db_session, follower_id=user1.id, followed_id=user2.id)

@pytest.mark.parametrize("non_existent_user_id", [
    uuid.uuid4(),
    None
])
def test_user_following_nonexistent_user(db_session, non_existent_user_id):
    """
    Test that following a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=user.id, followed_id=non_existent_user_id)

@pytest.mark.parametrize("non_existent_user_id", [
    uuid.uuid4(),
    None
])
def test_user_followed_by_nonexistent_user(db_session, non_existent_user_id):
    """
    Test that a non-existent user cannot follow a user.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_follow(db_session, follower_id=non_existent_user_id, followed_id=user.id)


# def test_user_cannot_follow_themselves(db_session):
#     """
#     Test that a user cannot follow themselves.
#     """
#     user = create_user(db_session, 'selfuser', 'selfuser@example.com', 'password123')
#     with pytest.raises(IntegrityError):
#         create_follow(db_session, follower_id=user.id, followed_id=user.id)


# -------------------------------
# Post Model Tests
# -------------------------------

@pytest.mark.parametrize("caption", [
    None,
    '',
    'Test Caption',
])
def test_create_post(db_session, caption):
    """
    Test creating a valid post.
    """
    user = create_user(db_session, 'postuser', 'postuser@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='This is a test post.', caption=caption)
    retrieved_post = db_session.query(Post).filter_by(id=post.id).first()
    assert retrieved_post == post


@pytest.mark.parametrize("owner_id", [
    uuid.uuid4(),
    None
])
def test_create_post_with_invalid_owner(db_session, owner_id):
    """
    Test that creating a post with invalid owner fails.
    """
    with pytest.raises(IntegrityError):
        create_post(db_session, owner_id=owner_id, content='Content without owner', caption='No Owner')


@pytest.mark.parametrize("content", [None])
def test_create_post_with_invalid_content(db_session, content):
    """
    Test that creating a post with empty content fails.
    """
    user = create_user(db_session, 'emptycontentuser', 'emptycontent@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_post(db_session, owner_id=user.id, content=content, caption='Empty Content')


def test_post_owner_relationship(db_session):
    """
    Test that a post is linked to its owner correctly.
    """
    user = create_user(db_session, 'owneruser', 'owneruser@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Owner\'s post', caption='Owner Caption')
    assert post.owner == user
    assert user.posts[0] == post


def test_delete_post_deletes_likes(db_session):
    """
    Test that deleting a post also deletes its likes due to cascade.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password1')
    post = create_post(db_session, owner_id=user.id, content='Post to be liked', caption='Like Test')
    like = create_post_like(db_session, user_id=user.id, post_id=post.id)
    db_session.delete(post)
    db_session.commit()
    deleted_like = db_session.query(PostLike).filter_by(id=like.id).first()
    assert deleted_like is None


def test_delete_post_deletes_comments(db_session):
    """
    Test that deleting a post also deletes its comments due to cascade.
    """
    user = create_user(db_session, 'cascadecommentuser', 'cascadecomment@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post to be deleted', caption='Cascade Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='This comment will be deleted.')
    db_session.delete(post)
    db_session.commit()
    # The comment should be deleted due to cascade
    deleted_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert deleted_comment is None


# -------------------------------
# Comment Model Tests
# -------------------------------

@pytest.mark.parametrize("use_same_user", [True, False])
def test_create_comment(db_session, use_same_user):
    """
    Test creating a valid comment on a post by either the post owner (self) or a different user.
    """
    user1 = create_user(db_session, 'commentuser', 'commentuser@example.com', 'password123')
    if use_same_user:
        user2 = user1  # user2 is the same as user1 (self-comment)
    else:
        user2 = create_user(db_session, 'otheruser', 'otheruser@example.com', 'password456')  # user2 is a different user
    post = create_post(db_session, owner_id=user1.id, content='Post for commenting', caption='Comment Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id, content='This is a test comment.')
    retrieved_comment = db_session.query(Comment).filter_by(id=comment.id).first()
    assert retrieved_comment == comment


@pytest.mark.parametrize("post_id", [
    uuid.uuid4(),
    None
])
def test_create_comment_with_invalid_post(db_session, post_id):
    """
    Test that creating a comment with invalid post fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=post_id, user_id=user.id, content='Comment without post')


@pytest.mark.parametrize("user_id", [
    uuid.uuid4(),
    None
])
def test_create_comment_with_notexistent_user(db_session, user_id):
    """
    Test that creating a comment without a user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for null user comment', caption='Null User Comment Test')
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=post.id, user_id=user_id, content='Comment without user')


@pytest.mark.parametrize("content", [None])
def test_create_comment_with_invalid_content(db_session, content):
    """
    Test that creating a comment with empty content fails.
    """
    user = create_user(db_session, 'emptycommentuser', 'emptycomment@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for empty comment', caption='Empty Comment Test')
    with pytest.raises(IntegrityError):
        create_comment(db_session, post_id=post.id, user_id=user.id, content=content)


def test_comment_owner_relationship(db_session):
    """
    Test that a comment is linked to its owner and post correctly.
    """
    user = create_user(db_session, 'commentowner', 'commentowner@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for relationship test', caption='Relationship Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='Relationship comment')
    assert comment.owner == user
    assert comment.post == post
    assert user.comments[0] == comment
    assert post.comments[0] == comment


def test_delete_comment_deletes_likes(db_session):
    """
    Test that deleting a comment also deletes its likes due to cascade.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password1')
    post = create_post(db_session, owner_id=user.id, content='Post for deleting comment likes', caption='Delete Comment Likes Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='Comment to delete likes')
    like = create_comment_like(db_session, user_id=user.id, comment_id=comment.id)
    db_session.delete(comment)
    db_session.commit()
    # The like should be deleted due to cascade
    deleted_like = db_session.query(CommentLike).filter_by(id=like.id).first()
    assert deleted_like is None


# -------------------------------
# PostLike Model Tests
# -------------------------------

@pytest.mark.parametrize("use_same_user", [True, False])
def test_post_like(db_session, use_same_user):
    """
    Test liking a valid post by either the same user (user1) or a different user (user2).
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    if use_same_user:
        user2 = user1  # user2 is the same as user1
    else:
        user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')  # user2 is a different user
    post = create_post(db_session, owner_id=user1.id, content='Post to be liked', caption='Post Like Test')
    post_like = create_post_like(db_session, user_id=user2.id, post_id=post.id)
    retrieved_like = db_session.query(PostLike).filter_by(id=post_like.id).first()
    assert retrieved_like.id == post_like.id
    assert retrieved_like.user == user2
    assert retrieved_like.post == post


# def test_unique_post_like(db_session):
#     """
#     Test that a user cannot like the same post more than once.
#     """
#     user = create_user(db_session, 'user', 'user@example.com', 'password123')
#     post = create_post(db_session, owner_id=user.id, content='Unique Like Post', caption='Unique Like Test')
#     create_post_like(db_session, user_id=user.id, post_id=post.id)
#     with pytest.raises(IntegrityError):
#         create_post_like(db_session, user_id=user.id, post_id=post.id)


@pytest.mark.parametrize("owner_id", [
    uuid.uuid4(),
    None
])
def test_create_post_like_with_nonexistent_user(db_session, owner_id):
    """
    Test that liking a post with a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for invalid user like', caption='Invalid User Like Test')
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=owner_id, post_id=post.id)


@pytest.mark.parametrize("post_id", [
    uuid.uuid4(),
    None
])
def test_create_post_like_with_nonexistent_post(db_session, post_id):
    """
    Test that liking a non-existent post fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_post_like(db_session, user_id=user.id, post_id=post_id)


# -------------------------------
# CommentLike Model Tests
# -------------------------------

@pytest.mark.parametrize("use_same_user", [True, False])
def test_comment_like(db_session, use_same_user):
    """
    Test liking a valid comment, either by the comment owner or another user.
    """
    user1 = create_user(db_session, 'user1', 'user1@example.com', 'password1')
    if use_same_user:
        user2 = user1  # user2 is the same as user1 (self-liking)
    else:
        user2 = create_user(db_session, 'user2', 'user2@example.com', 'password2')  # user2 is a different user
    post = create_post(db_session, owner_id=user1.id, content='Post for comment like', caption='Comment Like Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user2.id, content='Comment to be liked')
    comment_like = create_comment_like(db_session, user_id=user1.id, comment_id=comment.id)
    retrieved_like = db_session.query(CommentLike).filter_by(id=comment_like.id).first()
    assert retrieved_like is not None
    assert retrieved_like.user == user1
    assert retrieved_like.comment == comment


@pytest.mark.parametrize("user_id", [
    uuid.uuid4(),
    None
])
def test_create_comment_like_with_nonexistent_user(db_session, user_id):
    """
    Test that liking a comment with a non-existent user fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    post = create_post(db_session, owner_id=user.id, content='Post for invalid comment like', caption='Invalid Comment Like Test')
    comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='Comment for invalid like')
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=user_id, comment_id=comment.id)


@pytest.mark.parametrize("comment_id", [
    uuid.uuid4(),
    None
])
def test_create_comment_like_with_nonexistent_comment(db_session, comment_id):
    """
    Test that liking a non-existent comment fails.
    """
    user = create_user(db_session, 'user', 'user@example.com', 'password123')
    with pytest.raises(IntegrityError):
        create_comment_like(db_session, user_id=user.id, comment_id=comment_id)


# def test_unique_comment_like(db_session):
#     """
#     Test that a user cannot like the same comment more than once.
#     """
#     user = create_user(db_session, 'likeuser', 'likeuser@example.com', 'password123')
#     post = create_post(db_session, owner_id=user.id, content='Duplicate Comment Like Post', caption='Duplicate Comment Like Test')
#     comment = create_comment(db_session, post_id=post.id, user_id=user.id, content='Duplicate Comment')
#     create_comment_like(db_session, user_id=user.id, comment_id=comment.id)
#     with pytest.raises(IntegrityError):
#         create_comment_like(db_session, user_id=user.id, comment_id=comment.id)