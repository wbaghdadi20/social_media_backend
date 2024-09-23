from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserPrivate, UserNotFound
from ..crud.user_crud import get_user_by_login

def authenticate_user(login_data: UserCreate, db: Session) -> UserPrivate:
    user = get_user_by_login(login_data=login_data, db=db)
    if user is None:
        raise UserNotFound
    return UserPrivate.model_validate(user, strict=True)