from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from uuid import UUID
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from jwt.exceptions import ExpiredSignatureError
from typing import Annotated
from ..schemas import UserPrivate
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..crud import user_crud
from ..routes import db_dependency

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth2_scheme = HTTPBearer()

token_dependency = Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]

def create_access_token(data: dict, expire_date: timedelta | None = None):
    data["id"] = str(data["id"]) # convert UUID to string first 
    to_encode = data.copy()
    if expire_date is None:
        expire_date = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expire_date
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

async def get_current_user(credentials: token_dependency, db: db_dependency) -> UserPrivate:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("email")
        id: UUID = UUID(payload.get("id"))
        username: str = payload.get("username")
        if email is None or id is None or username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_id(user_id=id, db=db)
    if user is None:
        raise credentials_exception
    return UserPrivate.model_validate(user, strict=True)