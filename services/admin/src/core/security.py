import jwt
import datetime as dt

from passlib.context import CryptContext
from pydantic import Field
from typing import Annotated
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer

from src.core.config import BaseSchema, settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

passwrod_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Header(BaseSchema):
    alg: str = settings.JWT_ALGORITHM
    typ: str = "JWT"


class FullPayload(BaseSchema):
    sub: Annotated[str | None, Field(default=None)]
    exp: Annotated[int | None, Field(default=None)]
    type: str = "access"


def hash_password(password):
    return passwrod_context.hash(password)


def verify_password(password, hashed_password):
    return passwrod_context.verify(password, hashed_password)


def create_access_token(sub: str, expires_delta_minutes: int | None = None):
    if expires_delta_minutes is None:
        expires_delta_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=expires_delta_minutes)).timestamp()
    full_payload = FullPayload(sub=sub, exp=int(exp), type="access")
    
    access_token = jwt.encode(payload=full_payload.model_dump(), key=settings.JWT_SECRET_KEY,
                               algorithm=settings.JWT_ALGORITHM)
    return access_token


def create_refresh_token(sub: str, expires_delta_days: int | None = None):
    if expires_delta_days is None:
        expires_delta_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=expires_delta_days)).timestamp()
    full_payload = FullPayload(sub=sub, exp=int(exp), type="refresh")
    
    refresh_token = jwt.encode(payload=full_payload.model_dump(), key=settings.JWT_SECRET_KEY,
                                algorithm=settings.JWT_ALGORITHM)
    return refresh_token


def create_tokens(sub: str):
    access_token = create_access_token(sub)
    refresh_token = create_refresh_token(sub)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def decode_token(token: str):
    decoded_token = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
    return decoded_token

def get_token_from_request(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return auth_header.split()[1]
    return None
