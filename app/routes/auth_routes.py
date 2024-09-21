from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from app.services import auth_service
from ..schemas import Token, UserCreate
from ..config.database import get_db
from ..config.token import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]    
)

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/login", response_model=Token)
def login(login_data: UserCreate, db: db_dependency):

    # 1. Authenticate the user
    user = auth_service.authenticate_user(login_data=login_data, db=db)
    user_data = user.model_dump(exclude="created_at")

    # 2. Generate access token
    token = create_access_token(data=user_data)
    
    # 3. Return Token
    return Token (
        access_token=token,
        token_type="bearer"
    )