from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserPrivate, FollowBase, EmailAlreadyRegistered, UsernameAlreadyRegistered, UserNotFound, CannotFollowSelf, AlreadyFollowing, NotFollowing, CannotUnFollowSelf
from ..crud import user_crud as user_crud
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

# ----------- Setters ----------- #

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

def delete_user(user_to_delete: UserPrivate, db: Session) -> None:
    user_crud.delete_user(user_to_delete_id=user_to_delete.id, db=db)
    return

def follow_user(current_user: UserPrivate, username_to_follow: str, db: Session) -> FollowBase:
    
    # 1. See if username exists
    user_to_follow = user_crud.get_user_by_email_or_username(username=username_to_follow, db=db)

    # 2. If user doesnt exist, raise error
    if user_to_follow is None:
        raise UserNotFound
    
    # 3. If user is trying to follow themselves, 
    #    or if follow relationship already exists, raise error
    existing_follow = user_crud.get_follow(follower_id=current_user.id, followed_id=user_to_follow.id, db=db)
    if existing_follow:
        raise AlreadyFollowing
    if current_user.username == user_to_follow.username:
        raise CannotFollowSelf
    
    # 4. Follow user_to_follow
    follow_db = user_crud.follow_user(current_user_id=current_user.id, user_to_follow_id=user_to_follow.id, db=db)

    # 5. Return Follow
    return FollowBase.model_validate(follow_db, strict=True)

def unfollow_user(current_user: UserPrivate, username_to_unfollow: str, db: Session) -> None:
    
    # 1. See if username exists
    user_to_unfollow = user_crud.get_user_by_email_or_username(username=username_to_unfollow, db=db)

    # 2. If user doesn't exist, raise an error
    if user_to_unfollow is None:
        raise UserNotFound

    # 3. If user is trying to unfollow themselves, 
    #    or if follow relationship doesnt exists, raise error
    existing_follow = user_crud.get_follow(follower_id=current_user.id, followed_id=user_to_unfollow.id, db=db)
    if current_user.username == user_to_unfollow.username:
        raise CannotUnFollowSelf
    if not existing_follow:
        raise NotFollowing

    # 4. Delete the follow relationship from the database
    user_crud.unfollow_user(follow=existing_follow, db=db)

    return