from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

# Base model containing common user attributes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)

# Model for user creation (sign-up)
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(from_attributes=True)

# Model representing the user data stored in the database
class UserDB(UserCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Public model for exposing user information without sensitive data
class UserPublic(UserBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Private model for authenticated user details
class UserPrivate(UserPublic):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# Model representing the token structure
class Token(BaseModel):
    access_token: str
    token_type: str

# Model for token payload data
class TokenPayload(BaseModel):
    email: EmailStr
    id: UUID
    username: str

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