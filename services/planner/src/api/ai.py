"""AI Agent endpoints for OpenRouter integration."""
import base64
import io
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, File, Query, Request, UploadFile
from PIL import Image
from pydantic import BaseModel, Field

from src.core.config import BaseSchema, settings
from src.core.dependencies import db_dep, redis_dep
from src.schemas import task as task_schemas
from src.schemas.allocation import AllocationSchema
from src.services import (
    call_openrouter,
    run_chat_with_tools,
)
from src.services import (
    create_allocation_via_ai as create_allocation_service,
)
from src.services import (
    create_task_via_ai as create_task_service,
)

router = APIRouter(prefix="/ai", tags=["AI"])

logger = logging.getLogger("ai")


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    model: str = settings.OPENROUTER_DEFAULT_MODEL


class CreateTaskRequest(BaseModel):
    instruction: str
    model: str = settings.OPENROUTER_DEFAULT_MODEL


class CreateAllocationRequest(BaseModel):
    calendar_id: int
    instruction: str
    model: str = settings.OPENROUTER_DEFAULT_MODEL


async def _call_openrouter(
    messages: list[dict[str, Any]],
    model: str = settings.OPENROUTER_DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | None = None,
) -> dict[str, Any]:
    # Keep function alias in API module for backward-compatible test patching.
    return await call_openrouter(
        messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,
        tool_choice=tool_choice,
    )


@router.post("/chat")
async def chat(
    request: Request,
    session: db_dep,
    redis: redis_dep,
    payload: ChatRequest = Body(...),
) -> dict[str, Any]:
    user_id = request.state.user_id

    logger.info(f"Chat request from user {user_id}: {payload.message[:100]}...")
    return await run_chat_with_tools(
        user_id=user_id,
        message=payload.message,
        session=session,
        model=payload.model,
        llm_call=_call_openrouter,
        redis=redis,
        conversation_id=payload.conversation_id,
    )


@router.post("/create_task")
async def create_task_via_ai(
    request: Request,
    session: db_dep,
    payload: CreateTaskRequest = Body(...),
) -> task_schemas.TaskSchema:
    user_id = request.state.user_id
    return await create_task_service(
        user_id=user_id,
        instruction=payload.instruction,
        session=session,
        model=payload.model,
        llm_call=_call_openrouter,
    )


@router.post("/create_allocation")
async def create_allocation_via_ai(
    request: Request,
    session: db_dep,
    payload: CreateAllocationRequest = Body(...),
) -> AllocationSchema:
    user_id = request.state.user_id
    return await create_allocation_service(
        user_id=user_id,
        calendar_id=payload.calendar_id,
        instruction=payload.instruction,
        session=session,
        model=payload.model,
        llm_call=_call_openrouter,
    )


class ImageAnalysisResponseSchema(BaseSchema):
    """Response schema for image analysis endpoint."""
    image: str = Field(description="Base64 encoded image")
    format: str = Field(description="Image format (e.g., png, jpeg)")


@router.post("/analyze_image", response_model=ImageAnalysisResponseSchema)
async def analyze_image(
    request: Request,
    image: Annotated[UploadFile, File(description="Image file to analyze")],
) -> ImageAnalysisResponseSchema:
    """
    Analyze an uploaded image and return base64 encoded version.

    - Accepts multipart/form-data with image file
    - Returns base64 encoded image
    - Stateless operation, no disk storage
    """
    user_id = request.state.user_id

    if not image.content_type or not image.content_type.startswith("image/"):
        raise ValueError("File must be an image")

    image_bytes = await image.read()

    logger.info(f"Image analysis request from user {user_id}: {image.filename or 'unnamed'}")

    img = Image.open(io.BytesIO(image_bytes))

    output = io.BytesIO()
    img.save(output, format=img.format or "PNG")
    output.seek(0)

    base64_image = base64.b64encode(output.read()).decode("utf-8")

    return ImageAnalysisResponseSchema(
        image=base64_image,
        format=img.format or "PNG",
    )
