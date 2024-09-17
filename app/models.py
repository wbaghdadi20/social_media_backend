# app/models.py

import uuid
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint,
    CheckConstraint,
    Text,
)
from sqlalchemy.orm import relationship
from .config.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('username', name='uq_users_username'),
        UniqueConstraint('email', name='uq_users_email'),
        CheckConstraint('length(username) >= 3', name='ck_users_username_min_length'),
        CheckConstraint('length(username) <= 50', name='ck_users_username_max_length'),
        CheckConstraint('length(password_hash) >= 8', name='ck_users_password_min_length'),
        CheckConstraint("email LIKE '%@%.%'", name='ck_users_email_format'),
    )

    posts = relationship('Post', back_populates='owner', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='owner', cascade='all, delete-orphan')
    post_likes = relationship('PostLike', back_populates='user', cascade='all, delete-orphan')
    comment_likes = relationship('CommentLike', back_populates='user', cascade='all, delete-orphan')
    following = relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        back_populates='follower',
        cascade='all, delete-orphan'
    )
    followers = relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        back_populates='followed',
        cascade='all, delete-orphan'
    )

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    caption = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('length(content) >= 1', name='ck_posts_content_min_length'),
        CheckConstraint('length(caption) <= 255', name='ck_posts_caption_max_length'),
    )

    owner = relationship('User', back_populates='posts')
    likes = relationship('PostLike', back_populates='post', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')

class PostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_post_likes_user_post'),
    )

    user = relationship('User', back_populates='post_likes')
    post = relationship('Post', back_populates='likes')

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('length(content) >= 1', name='ck_comments_content_min_length'),
    )

    post = relationship('Post', back_populates='comments')
    owner = relationship('User', back_populates='comments')
    likes = relationship('CommentLike', back_populates='comment', cascade='all, delete-orphan')

class CommentLike(Base):
    __tablename__ = 'comment_likes'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    comment_id = Column(String(36), ForeignKey('comments.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'comment_id', name='uq_comment_likes_user_comment'),
    )

    user = relationship('User', back_populates='comment_likes')
    comment = relationship('Comment', back_populates='likes')

class Follow(Base):
    __tablename__ = 'follows'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    followed_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='uq_follows_follower_followed'),
        CheckConstraint('follower_id != followed_id', name='ck_follows_no_self_follow'),
    )

    follower = relationship('User', foreign_keys=[follower_id], back_populates='following')
    followed = relationship('User', foreign_keys=[followed_id], back_populates='followers')
