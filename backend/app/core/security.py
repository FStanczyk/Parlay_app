from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)

    if len(plain_password) > 72:
        plain_password = plain_password[:72]

    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        while len(password_bytes) > 72:
            password_bytes = password_bytes[:-1]
        plain_password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")
        while len(password.encode("utf-8")) > 72 and len(password) > 0:
            password = password[:-1]

    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception


def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise credentials_exception
    email = verify_token(access_token, credentials_exception)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        email = verify_token(access_token, credentials_exception)
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception:
        return None
