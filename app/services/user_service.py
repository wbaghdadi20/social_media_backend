from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..schemas import UserCreate, UserPrivate, EmailAlreadyRegistered, UsernameAlreadyRegistered, UserNotFound
from ..crud import user_crud as user_crud
from uuid import UUID

pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated="auto")

def verify_password(plain_pass, hashed_pass) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

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

def get_user_by_id(user_id: UUID, db=Session):

    # 1. Check if user exists
    user_db = user_crud.get_user_by_id(user_id=user_id, db=db)

    # 2. If user doesnt exist, raise error
    if user_db is None:
        print("here")
        raise UserNotFound
    
    # 3. Return User
    return user_db