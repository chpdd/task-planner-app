from fastapi import FastAPI

from src.api import api_router
from src.core.middleware import middleware

app = FastAPI(
    root_path="/api/planner",
    middleware=middleware,
    swagger_ui_parameters={"persistAuthorization": True},
)
app.include_router(api_router)
