from fastapi import Depends, APIRouter, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from ..services import user_service, auth_service
from ..schemas import Token, UserCreate, UserNotFound, EmailAlreadyRegistered, UsernameAlreadyRegistered
from ..config.database import get_db
from ..config.token import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]    
)

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/signup", response_model=Token, description="Creates a new user account with the provided data and returns an access token for authentication.")
def create_user(user_create: UserCreate, db: db_dependency):
    
    # 1. Create User 
    try:
        user = auth_service.create_user(user_create=user_create, db=db)
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


@router.post("/login", response_model=Token, description="Authenticates a user with their email and password. Returns an access token if the credentials are correct.")
def login(login_data: UserCreate, db: db_dependency):

    # 1. Authenticate the user
    try:
        user = auth_service.authenticate_user(login_data=login_data, db=db)
    except UserNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    user_data = user.model_dump(exclude="created_at")

    # 2. Generate access token
    token = create_access_token(data=user_data)
    
    # 3. Return Token
    return Token (
        access_token=token,
        token_type="bearer"
    )