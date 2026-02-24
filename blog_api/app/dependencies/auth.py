from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings
from app.database import supabase
from app.models.user import TokenData, UserResponse
from app.crud.user import get_user_by_id


# Tells FastAPI:
#   - Clients send the token in Authorization: Bearer <token>
#   - The endpoint to GET a token is at /auth/login
#   - Swagger UI shows an "Authorize" button that uses this URL automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT.

    `data` should be {"sub": user_id}.
    "sub" (subject) is the standard JWT claim for who the token represents.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify a JWT.
    Returns TokenData if valid, None if expired, tampered, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return TokenData(user_id=user_id)
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    FastAPI dependency. Call with Depends(get_current_user) in any route.

    Extracts the Bearer token → decodes it → looks up the user in the DB.
    Raises 401 if the token is missing, invalid, expired, or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception

    user = get_user_by_id(supabase, token_data.user_id)
    if user is None:
        raise credentials_exception

    return UserResponse(**user)
