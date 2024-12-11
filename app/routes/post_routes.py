import boto3
from uuid import UUID
from fastapi import Depends, UploadFile, APIRouter, File, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from ..services import post_service
from ..schemas import PostBase, PostOut, UserPrivate, NotPostOwner, PostDoesntExist
from ..config.token import get_current_user
from ..config.database import get_db
from ..config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserPrivate, Depends(get_current_user)]
media_file_dependency = Annotated[List[UploadFile], File(...)]

@router.post("/new_post", response_model=PostOut, description="Create a new post by uploading 1 or more media files")
async def create_post(
    user: user_dependency,
    media_files: media_file_dependency,
    db: db_dependency,
    caption: Optional[str] = Query(None),
):
    validated_data = PostBase(caption=caption)
    try:
        post = post_service.create_post_record(owner_id=user.id, db=db, caption=validated_data.caption)
        uploaded_files = await post_service.process_media_files(
            post_id=post.id,
            media_files=media_files,
            s3_client=s3_client,
            db=db
        )
        post.media = uploaded_files   
        post.caption = validated_data.caption
        return post
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create post: {str(e)}"
        )

@router.delete("/remove_post/{post_id}", description="Delete a post")
async def delete_post(
    user: user_dependency,
    db: db_dependency,
    post_id: UUID
):
    try:
        response = await post_service.delete_post(user_id=user.id, post_id=post_id, db=db, s3_client=s3_client)
    except PostDoesntExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except NotPostOwner as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    
    return response
