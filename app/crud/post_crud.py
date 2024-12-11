from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Post, Media


def create_post_record(owner_id: UUID, db: Session, caption: str | None = None) -> Post:
    post = Post(owner_id=owner_id, caption=caption)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def create_media_record(post_id: UUID, media_type: str, file_path: str, db: Session) -> Media:
    media = Media(post_id=post_id, media_type=media_type, file_path=file_path)
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

def get_post_by_id(post_id: UUID, db: Session) -> Post:
    return db.query(Post).filter(Post.id == post_id).first()

def delete_post(post: Post, db: Session) -> Post:
    db.delete(post)
    db.commit()