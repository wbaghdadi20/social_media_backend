from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserPrivate, UserNotFound, EmailAlreadyRegistered, UsernameAlreadyRegistered
from ..crud import user_crud

def authenticate_user(login_data: UserCreate, db: Session) -> UserPrivate:
    user = user_crud.get_user_by_login(login_data=login_data, db=db)
    if user is None:
        raise UserNotFound
    return UserPrivate.model_validate(user, strict=True)

def create_user(user_create: UserCreate, db: Session) -> UserPrivate:
    
    # 1. Check if user exists
    existing_user = user_crud.get_user_by_email_or_username(email=user_create.email, username=user_create.username, db=db)

    # 2. If user exists, raise error
    if existing_user:
        if existing_user.email == user_create.email:
            raise EmailAlreadyRegistered
        raise UsernameAlreadyRegistered
    
    # 3. Create user and hash password
    user_db = user_crud.create_user(user_create=user_create, db=db)

    # 4. Return User
    return UserPrivate.model_validate(user_db, strict=True)