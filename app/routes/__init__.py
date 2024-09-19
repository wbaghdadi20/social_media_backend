from fastapi import Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from typing import Annotated

db_dependency = Annotated[Session, Depends(get_db)]
