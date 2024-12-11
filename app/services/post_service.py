import asyncio
import functools
from uuid import UUID, uuid4
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from botocore.exceptions import ClientError
from ..schemas import PostOut, MediaOut, NotPostOwner, PostDoesntExist
from ..config.config import BUCKET_NAME
from ..crud import post_crud

def identify_media_type(file_extension: str) -> str:
    image_extensions = {"jpg", "jpeg", "png", "gif"}
    video_extensions = {"mp4", "avi", "mov", "mkv"}

    if file_extension.lower() in image_extensions:
        return "image"
    elif file_extension.lower() in video_extensions:
        return "video"
    else:
        return "other"

async def process_media_files(
    post_id: UUID,
    media_files: List[UploadFile],
    s3_client,
    db: Session
) -> List[MediaOut]:
    
    uploaded_files = []
    try:
        for file in media_files:
            # Generate unique file name
            file_ext = file.filename.split('.')[-1]
            file_name = f"{uuid4()}.{file_ext}"

            # Identify media type
            media_type = identify_media_type(file_ext)

            # Upload to S3
            s3_client.upload_fileobj(
                file.file,
                BUCKET_NAME,
                file_name,
                ExtraArgs={"ContentType": file.content_type}
            )

            # Construct file URL
            bucket_region = s3_client.get_bucket_location(Bucket=BUCKET_NAME)['LocationConstraint']
            file_url = f"https://{BUCKET_NAME}.s3.{bucket_region}.amazonaws.com/{file_name}"

            # Create media record
            media_record_db = post_crud.create_media_record(
                post_id=post_id,
                media_type=media_type,
                file_path=file_url,
                db=db
            )

            media_record_out = MediaOut.model_validate(media_record_db, strict=True)
            uploaded_files.append(media_record_out)

    except ClientError as e:
        db.rollback()   
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process media files: {e.response['Error']['Message']}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

    return uploaded_files

def create_post_record(owner_id: UUID, db: Session, caption: str | None = None) -> PostOut:
    post_db = post_crud.create_post_record(owner_id=owner_id, db=db, caption=caption)
    return PostOut.model_validate(post_db, strict=True)

async def delete_post(user_id: UUID, post_id: UUID, db: Session, s3_client):
    post_db = post_crud.get_post_by_id(post_id=post_id, db=db)

    if post_db is None:
        raise PostDoesntExist
    if post_db.owner_id != user_id:
        raise NotPostOwner

    # Prepare the list of keys for deletion
    bucket_region = s3_client.get_bucket_location(Bucket=BUCKET_NAME)['LocationConstraint']
    keys = [{"Key": media.file_path.split(f"s3.{bucket_region}.amazonaws.com/")[-1]} for media in post_db.media]

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            functools.partial(
                s3_client.delete_objects,
                Bucket=BUCKET_NAME,
                Delete={"Objects": keys},
            ),
        )
    except Exception as e:
        raise Exception(f"Failed to delete media files from S3: {str(e)}")

    # Delete the post from the database
    post_crud.delete_post(post=post_db, db=db)

    return response