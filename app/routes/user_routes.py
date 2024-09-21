from fastapi import Depends, APIRouter, HTTPException, status
from typing import Annotated
from ..services import user_service
from ..schemas import UserCreate, Token, UserPrivate
from ..config.token import get_current_user, create_access_token
from uuid import UUID
import re
from . import db_dependency

router = APIRouter(
    prefix="/users",
    tags=["Users"]    
)

UUID_PATTERN = re.compile(r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$")

def normalize_uuid(user_id: str) -> UUID:
    try:
        # Check if the user_id is 32 characters long (without hyphens)
        if len(user_id) == 32:
            # Add hyphens to convert it into a valid UUID format
            user_id = f"{user_id[:8]}-{user_id[8:12]}-{user_id[12:16]}-{user_id[16:20]}-{user_id[20:]}"
        
        # Check if the user_id is 36 characters long and matches the UUID pattern
        if len(user_id) == 36 and UUID_PATTERN.match(user_id):
            # Convert the string into a UUID object
            return UUID(user_id)
        else:
            raise ValueError  # If format doesn't match, raise an error
    
    except ValueError:
        # Raise an HTTP 400 Bad Request error if the UUID is invalid
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format")

# Reusable dependencies
normalizedUUID = Annotated[UUID, Depends(normalize_uuid)]

@router.get("/me", response_model=UserPrivate)
def get_self(current_user: UserPrivate = Depends(get_current_user)):
    return current_user


@router.post("/signup", response_model=Token)
def create_user(user_create: UserCreate, db: db_dependency):
    
    # 1. Create User 
    user = user_service.create_user(user_create=user_create, db=db)
    user_data = user.model_dump(exclude="created_at")
    
    # 2. Generate Access Token
    token = create_access_token(data=user_data)
    
    # 3. Return Token
    return Token(
        access_token=token,
        token_type="bearer"
    )