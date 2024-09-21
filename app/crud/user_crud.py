from sqlalchemy.orm import Session
from ..models import User
from ..schemas import UserCreate
from ..services.user_service import verify_password, get_hashed_password
from uuid import UUID

def get_user_by_id(user_id: UUID, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_email_or_username(email: str, username: str, db: Session) -> User:
    return db.query(User).filter((User.email == email) | (User.username == username)).first()

def get_user_by_login(login_data: UserCreate, db: Session) -> User:
    user = db.query(User).filter(User.email == login_data.email, User.username == login_data.username).first()
    if user and verify_password(login_data.password, user.password):
        return user
    return None

def create_user(user_create: UserCreate, db: Session) -> User:
    user_db = User(**user_create.model_dump())
    user_db.password = get_hashed_password(user_db.password)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db