from fastapi import Depends, APIRouter, HTTPException, status
from ..services import user_service
from ..schemas import UserCreate, Token, UserPrivate, EmailAlreadyRegistered, UsernameAlreadyRegistered
from ..config.token import get_current_user, create_access_token
from uuid import UUID
import re
from . import db_dependency

router = APIRouter(
    prefix="/users",
    tags=["Users"]    
)

@router.get("/me", response_model=UserPrivate)
def get_self(current_user: UserPrivate = Depends(get_current_user)):
    return current_user


@router.post("/signup", response_model=Token)
def create_user(user_create: UserCreate, db: db_dependency):
    
    # 1. Create User 
    try:
        user = user_service.create_user(user_create=user_create, db=db)
    except (EmailAlreadyRegistered, UsernameAlreadyRegistered) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    user_data = user.model_dump(exclude="created_at")
    
    # 2. Generate Access Token
    token = create_access_token(data=user_data)
    
    # 3. Return Token
    return Token(
        access_token=token,
        token_type="bearer"
    )