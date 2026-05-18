from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.api import api_router
from src.core.exceptions import RowNotFoundError
from src.core.middleware import middleware
from src.core.redis import redis_service
from src.core.security import oauth2_scheme

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_service.connect()
    yield
    # Shutdown
    await redis_service.close()

app = FastAPI(
    root_path="/api/planner",
    title="Planner Service",
    middleware=middleware,
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan,
    dependencies=[Depends(oauth2_scheme)]
)
app.include_router(api_router)


@app.exception_handler(RowNotFoundError)
async def row_not_found_handler(_: Request, exc: RowNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
