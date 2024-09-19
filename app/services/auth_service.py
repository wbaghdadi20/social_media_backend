from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserPrivate
from ..crud.user_crud import get_user_by_login

def authenticate_user(login_data: UserCreate, db: Session) -> UserPrivate:
    user = get_user_by_login(login_data=login_data, db=db)
    print("Authenticating user")
    # print(vars(user))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserPrivate.model_validate(user, strict=True)