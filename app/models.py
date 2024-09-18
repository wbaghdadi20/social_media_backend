import uuid
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    func,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .config.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(), unique=True, nullable=False, index=True)
    email = Column(String(), unique=True, nullable=False, index=True)
    password_hash = Column(String(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship('Post', back_populates='owner', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='owner', cascade='all, delete-orphan')
    post_likes = relationship('PostLike', back_populates='user', cascade='all, delete-orphan')
    comment_likes = relationship('CommentLike', back_populates='user', cascade='all, delete-orphan')
    following = relationship(
        'Follow', foreign_keys='Follow.follower_id', back_populates='follower', cascade='all, delete-orphan'
    )
    followers = relationship(
        'Follow',foreign_keys='Follow.followed_id',back_populates='followed',cascade='all, delete-orphan'
    )

class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    caption = Column(String(), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship('User', back_populates='posts')
    likes = relationship('PostLike', back_populates='post', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')

class PostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='post_likes')
    post = relationship('Post', back_populates='likes')

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship('Post', back_populates='comments')
    owner = relationship('User', back_populates='comments')
    likes = relationship('CommentLike', back_populates='comment', cascade='all, delete-orphan')

class CommentLike(Base):
    __tablename__ = 'comment_likes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='comment_likes')
    comment = relationship('Comment', back_populates='likes')

class Follow(Base):
    __tablename__ = 'follows'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    followed_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    follower = relationship('User', foreign_keys=[follower_id], back_populates='following')
    followed = relationship('User', foreign_keys=[followed_id], back_populates='followers')
