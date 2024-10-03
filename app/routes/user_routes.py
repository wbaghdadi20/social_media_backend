from fastapi import Depends, Query, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from ..services import user_service
from ..schemas import FollowBase, UserPrivate, UserNotFound, AlreadyFollowing, CannotFollowSelf, NotFollowing, CannotUnFollowSelf
from ..config.token import get_current_user
from ..config.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserPrivate, Depends(get_current_user)]
username = Annotated[str, Query(title="Username of user trying to follow", min_length=3, max_length=50)]

@router.get("/me", response_model=UserPrivate, description="Returns the profile information of the currently authenticated user.")
def get_self(current_user: user_dependency):
    return current_user


@router.delete("/delete", response_model=dict, description="Deletes the currently authenticated user account. The user must be logged in to delete their account.")
def delete_user(current_user: user_dependency, db: db_dependency):
    user_service.delete_user(user_to_delete=current_user, db=db)
    return {"message": f"{current_user.username} successfully deleted"}


@router.post("/follow", response_model=FollowBase, description="Allows the current authenticated user to follow another user by specifying their username. Returns the follow relationship data.")
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


@router.delete("/unfollow", response_model=dict, description="Allows the current authenticated user to unfollow another user by specifying their username. Returns a confirmation message if the operation is successful.")
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