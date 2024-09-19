from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
import socket
from . import models
from .config.database import engine, get_db
from .routes.auth_routes import router as auth_router
from .routes.user_routes import router as user_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Backend API",
    description="API for managing social media backend services",
    version="1.0.0",
    openapi_tags=[
        {"name": "System", "description": "System-level endpoints for health and instance information"}
    ]
)

def delete_users(db: Session):
    try:
        db.query(models.User).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=f"Failed to delete all users. {str(e)}")
    
def get_users(db: Session):
    return db.query(models.User).all()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", tags=["System"])
def read_root():
    return {"message": "Welcome to the Social Media Backend API"}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

@app.get("/instance", tags=["System"])
def get_instance():
    hostname = socket.gethostname()
    return {"instance": hostname}

@app.delete("/delete-all-users", tags=["System"], description="Helper to delete all users easily")
def delete_all_users(db: db_dependency):
    delete_users(db=db)
    return {"message": "All users deleted successfully"}

@app.get("/get-all-users", tags=["System"], description="Helper to get all users easily")
def get_all_users(db: db_dependency):
    return get_users(db=db)


app.include_router(user_router)
app.include_router(auth_router)