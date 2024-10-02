from sqlalchemy.orm import Session
from ..models import User, Follow
from ..schemas import UserCreate
from app.utils import verify_password, get_hashed_password
from uuid import UUID

# ----------- Getters ----------- #

def get_user_by_id(user_id: UUID, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email_or_username(
    db: Session,
    email: str | None = None,
    username: str | None = None
) -> User:
    return db.query(User).filter((User.email == email) | (User.username == username)).first()

def get_user_by_login(login_data: UserCreate, db: Session) -> User:
    user = db.query(User).filter(User.email == login_data.email, User.username == login_data.username).first()
    if user and verify_password(login_data.password, user.password):
        return user
    return None

def get_follow(follower_id: UUID, followed_id: UUID, db: Session) -> Follow:
    return db.query(Follow).filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id).first()

# ----------- Setters ----------- #

def create_user(user_create: UserCreate, db: Session) -> User:
    user_db = User(**user_create.model_dump())
    user_db.password = get_hashed_password(user_db.password)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

def delete_user(user_to_delete_id: UUID, db: Session) -> None:
    db.query(User).filter(User.id == user_to_delete_id).delete()
    db.commit()

def follow_user(current_user_id: UUID, user_to_follow_id: UUID, db: Session) -> Follow:
    follow_db = Follow(
        follower_id=current_user_id,
        followed_id=user_to_follow_id
    )
    db.add(follow_db)
    db.commit()
    db.refresh(follow_db)
    return follow_db

def unfollow_user(follow: Follow, db: Session) -> None:
    db.delete(follow)
    db.commit()