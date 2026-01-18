from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.core import security
from src.core.dependencies import db_dep

from src.models import User
from src.crud import user_crud
from src.schemas import auth

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(auth_schema: auth.AuthSchema, session: db_dep):
    existing_user = await user_crud.schema_get_by_name(session, auth_schema.name)
    if existing_user is not None:
        raise HTTPException(detail="This name is already taken", status_code=status.HTTP_409_CONFLICT)

    hashed_password = security.hash_password(auth_schema.password)
    user = User(hashed_password=hashed_password, name=auth_schema.name)
    await user_crud.create(session, user)
    await session.commit()
    return security.create_tokens(str(user.id))


@router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     session: db_dep):
    user = await user_crud.get_by_name(session, form_data.username)

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this name and password not found")
    return security.create_tokens(str(user.id))


@router.post("/refresh")
async def refresh_access_token(refresh_schema: auth.RefreshTokenSchema):
    payload = security.decode_token(refresh_schema.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    new_access_token = security.create_access_token(sub=user_id)
    return {"access_token": new_access_token, "token_type": "bearer"}
