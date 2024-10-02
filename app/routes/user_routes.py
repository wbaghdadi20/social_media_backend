from fastapi import Depends, Query, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from ..services import user_service
from ..schemas import UserCreate, FollowBase, Token, UserPrivate, EmailAlreadyRegistered, UsernameAlreadyRegistered, UserNotFound, AlreadyFollowing, CannotFollowSelf, NotFollowing, CannotUnFollowSelf
from ..config.token import get_current_user, create_access_token
from ..config.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]    
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserPrivate, Depends(get_current_user)]
username = Annotated[str, Query(title="Username of user trying to follow", min_length=3, max_length=50)]

@router.get("/me", response_model=UserPrivate)
def get_self(current_user: user_dependency):
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


@router.delete("/delete", response_model=dict)
def delete_user(current_user: user_dependency, db: db_dependency):
    user_service.delete_user(user_to_delete=current_user, db=db)
    return {"message": f"{current_user.username} successfully deleted"}


@router.post("/follow", response_model=FollowBase)
def follow_user(
    current_user: user_dependency,
    username_to_follow: username,
    db: db_dependency
):
    try:
        follow = user_service.follow_user(current_user=current_user, username_to_follow=username_to_follow, db=db)
    except UserNotFound as exc:
        print("HELLO WORLD")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except (AlreadyFollowing, CannotFollowSelf) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)

    return follow


@router.delete("/unfollow", response_model=dict)
def unfollow_user(
    current_user: user_dependency,
    username_to_unfollow: username,
    db: db_dependency
):
    try:
        user_service.unfollow_user(current_user=current_user, username_to_unfollow=username_to_unfollow, db=db)
    except UserNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except (NotFollowing, CannotUnFollowSelf) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)

    return {"message": f"{current_user.username} successfully unfollowed {username_to_unfollow}"}