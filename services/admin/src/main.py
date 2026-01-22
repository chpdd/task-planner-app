from fastapi import FastAPI, Depends

from src.api import api_router
from src.core.middleware import middleware
from src.core.security import oauth2_scheme

app = FastAPI(
    root_path="/api/admin",
    title="Admin Service",
    middleware=middleware,
    swagger_ui_parameters={"persistAuthorization": True},
    dependencies=[Depends(oauth2_scheme)]
)
app.include_router(api_router)
