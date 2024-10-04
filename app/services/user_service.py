from sqlalchemy.orm import Session
from ..schemas import UserBase, UserPrivate, FollowBase, UserNotFound, CannotFollowSelf, AlreadyFollowing, NotFollowing, CannotUnFollowSelf
from ..crud import user_crud
from uuid import UUID

# ----------- Getters ----------- #

def get_user_by_id(user_id: UUID, db=Session) -> UserPrivate:

    # 1. Check if user exists
    user_db = user_crud.get_user_by_id(user_id=user_id, db=db)

    # 2. If user doesnt exist, raise error
    if user_db is None:
        raise UserNotFound
    
    # 3. Return UserPrivate
    return UserPrivate.model_validate(user_db, strict=True)

def _check_if_user_exists(username: str, db: Session):
    user = user_crud.get_user_by_email_or_username(username=username, db=db)
    if user is None:
        raise UserNotFound
    return user

def view_following(username: str, db: Session) -> list[UserBase]:
    
    user = _check_if_user_exists(username=username, db=db)
    
    lst_follow_db = user_crud.get_following(follower_id=user.id, db=db)
    lst_following = [
        UserBase.model_validate(
            user_crud.get_user_by_id(user_id=follow.followed_id, db=db)
        ) 
        for follow in lst_follow_db
    ]
    return lst_following

def view_followers(username: str, db: Session) -> list[UserBase]:
    
    user = _check_if_user_exists(username=username, db=db)
    
    lst_follow_db = user_crud.get_followers(followed_id=user.id, db=db)
    lst_followers = [
        UserBase.model_validate(
            user_crud.get_user_by_id(user_id=follow.follower_id, db=db)
        ) 
        for follow in lst_follow_db
    ]
    return lst_followers
    
# ----------- Setters ----------- #

def delete_user(user_to_delete: UserPrivate, db: Session) -> None:
    user_crud.delete_user(user_to_delete_id=user_to_delete.id, db=db)
    return

def follow_user(current_user: UserPrivate, username_to_follow: str, db: Session) -> FollowBase:
    
    user_to_follow = _check_if_user_exists(username=username_to_follow, db=db)
    
    # 3. If user is trying to follow themselves, 
    #    or if follow relationship already exists, raise error
    existing_follow = user_crud.get_specific_follow(follower_id=current_user.id, followed_id=user_to_follow.id, db=db)
    if existing_follow:
        raise AlreadyFollowing
    if current_user.username == user_to_follow.username:
        raise CannotFollowSelf
    
    # 4. Follow user_to_follow
    follow_db = user_crud.follow_user(current_user_id=current_user.id, user_to_follow_id=user_to_follow.id, db=db)

    # 5. Return Follow
    return FollowBase.model_validate(follow_db, strict=True)

def unfollow_user(current_user: UserPrivate, username_to_unfollow: str, db: Session) -> None:
    
    user_to_unfollow = _check_if_user_exists(username=username_to_unfollow, db=db)

    # 3. If user is trying to unfollow themselves, 
    #    or if follow relationship doesnt exists, raise error
    existing_follow = user_crud.get_specific_follow(follower_id=current_user.id, followed_id=user_to_unfollow.id, db=db)
    if current_user.username == user_to_unfollow.username:
        raise CannotUnFollowSelf
    if not existing_follow:
        raise NotFollowing

    # 4. Delete the follow relationship from the database
    user_crud.unfollow_user(follow=existing_follow, db=db)

    return