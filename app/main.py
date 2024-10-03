from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, selectinload
from typing import Annotated
import socket
from . import models
from .config.database import engine, get_db
from .routes.auth_routes import router as auth_router
from .routes.user_routes import router as user_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Backend API",
    description="API for managing social media backend services, including user authentication, post management, and social interactions.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "System", 
            "description": "System-level endpoints for health checks, instance information, and basic API operations."
        },
        {
            "name": "Users", 
            "description": "Routes to handle all user-related actions"
        },
        {
            "name": "Auth", 
            "description": "Routes to handle user authentication and managing access tokens."
        }
    ]
)

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", tags=["System"], description="Provides a welcome message and confirms that the API is running.")
def read_root():
    return {"message": "Welcome to the Social Media Backend API"}

@app.get("/instance", tags=["System"], description="Returns the hostname of the current instance for load balancing checks. Use this route to verify which server instance is handling the request (2 instances).")
def get_instance():
    hostname = socket.gethostname()
    return {"instance": hostname}

app.include_router(user_router)
app.include_router(auth_router)