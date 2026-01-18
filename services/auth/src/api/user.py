from fastapi import Depends, APIRouter, Request

from src.core.dependencies import db_dep

from src.core.security import oauth2_scheme
from src.crud import user_crud
from src.schemas import user

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(oauth2_scheme)])


@router.get("/me")
async def get_mine_user(request: Request, session: db_dep) -> user.UserSchema:
    return await user_crud.schema_get(session, request.state.user_id)


@router.get("")
async def list_users(session: db_dep) -> list[user.UserSchema]:
    return await user_crud.schema_list(session)


@router.get("/{user_id}")
async def get_user(user_id: int, session: db_dep):
    return await user_crud.schema_get(session, user_id)
