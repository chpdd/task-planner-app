import jwt
import datetime as dt
import fastapi.security

from passlib.context import CryptContext
from pydantic import Field
from typing import Annotated

from src.core.config import BaseSchema, settings

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Header(BaseSchema):
    alg: str = settings.JWT_ALGORITHM
    typ: str = "JWT"


class FullPayload(BaseSchema):
    sub: Annotated[str | None, Field(default=None)]
    exp: Annotated[int | None, Field(default=None)]
    type: str = "access"


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_access_token(sub: str, expires_delta_minutes: int | None = None):
    if expires_delta_minutes is None:
        expires_delta_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=expires_delta_minutes)).timestamp()
    full_payload = FullPayload(sub=sub, exp=int(exp), type="access")
    
    access_token = jwt.encode(payload=full_payload.model_dump(), key=settings.JWT_SECRET_KEY,
                               algorithm=settings.JWT_ALGORITHM)
    return access_token


def decode_token(token: str):
    try:
        decoded_token = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        return decoded_token
    except jwt.ExpiredSignatureError:
        error_msg = "Token has expired"
        raise jwt.PyJWTError(error_msg)
    except jwt.InvalidTokenError:
        error_msg = "Invalid token"
        raise jwt.PyJWTError(error_msg)

