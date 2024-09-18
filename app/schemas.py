from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserInDB(UserBase):
    id: UUID
    password: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserOut(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    content: str = Field(..., min_length=1)
    caption: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostLikeBase(BaseModel):
    user_id: UUID
    post_id: UUID

class PostLikeCreate(PostLikeBase):
    pass

class PostLikeOut(PostLikeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: UUID
    post_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommentLikeBase(BaseModel):
    user_id: UUID
    comment_id: UUID

class CommentLikeCreate(CommentLikeBase):
    pass

class CommentLikeOut(CommentLikeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FollowBase(BaseModel):
    follower_id: UUID
    followed_id: UUID

class FollowCreate(FollowBase):
    pass

class FollowOut(FollowBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
