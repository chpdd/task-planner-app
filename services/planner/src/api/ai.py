"""AI Agent endpoints for OpenRouter integration."""
import base64
import datetime as dt
import io
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel, Field
from sqlalchemy import select

from src.core.config import BaseSchema, settings
from src.core.dependencies import db_dep, redis_dep
from src.models import AIConversation, AIMessage
from src.schemas import task as task_schemas
from src.schemas.allocation import AllocationSchema
from src.services import (
    call_openrouter,
    run_chat_stream,
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
    image_base64: str | None = None
    image_mime: str = "image/png"


class CreateTaskRequest(BaseModel):
    instruction: str


class CreateAllocationRequest(BaseModel):
    calendar_id: int
    instruction: str


class ChatStreamRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    image_base64: str | None = None
    image_mime: str = "image/png"


class AIConversationSchema(BaseSchema):
    id: int
    title: str | None
    created_at: dt.datetime
    updated_at: dt.datetime


class AIMessageSchema(BaseSchema):
    role: str
    content: str
    created_at: dt.datetime


@router.get("/conversations", response_model=list[AIConversationSchema])
async def list_conversations(
    request: Request,
    session: db_dep,
) -> Any:
    user_id = request.state.user_id
    stmt = (
        select(AIConversation)
        .where(AIConversation.user_id == user_id)
        .order_by(AIConversation.updated_at.desc())
    )
    conversations = (await session.scalars(stmt)).all()
    return conversations


@router.get("/conversations/{conversation_id}/messages", response_model=list[AIMessageSchema])
async def list_messages(
    request: Request,
    conversation_id: int,
    session: db_dep,
) -> Any:
    user_id = request.state.user_id
    # Verify ownership
    stmt = select(AIConversation).where(
        AIConversation.id == conversation_id,
        AIConversation.user_id == user_id
    )
    conv = await session.scalar(stmt)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_stmt = (
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at.asc())
    )
    messages = (await session.scalars(msg_stmt)).all()
    # Filter out tool messages for the UI
    return [m for m in messages if m.role in ("user", "assistant")]


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
    user_content: Any = payload.message
    if payload.image_base64:
        user_content = [
            {"type": "text", "text": payload.message},
            {"type": "image_url", "image_url": {"url": f"data:{payload.image_mime};base64,{payload.image_base64}"}},
        ]

    logger.info(f"Chat request from user {user_id}: {payload.message[:100]}...")
    return await run_chat_with_tools(
        user_id=user_id,
        message=payload.message,
        session=session,
        model=settings.OPENROUTER_DEFAULT_MODEL,
        llm_call=_call_openrouter,
        redis=redis,
        conversation_id=payload.conversation_id,
        user_content=user_content,
    )


@router.post("/chat_stream")
async def chat_stream(
    request: Request,
    session: db_dep,
    redis: redis_dep,
    payload: ChatStreamRequest = Body(...),
) -> StreamingResponse:
    user_id = request.state.user_id
    user_content: Any = payload.message
    if payload.image_base64:
        user_content = [
            {"type": "text", "text": payload.message},
            {"type": "image_url", "image_url": {"url": f"data:{payload.image_mime};base64,{payload.image_base64}"}},
        ]

    logger.info(f"Chat stream request from user {user_id}: {payload.message[:100]}...")
    conv_id, token_stream = await run_chat_stream(
        user_id=user_id,
        message=payload.message,
        session=session,
        model=settings.OPENROUTER_DEFAULT_MODEL,
        conversation_id=payload.conversation_id,
        user_content=user_content,
        redis=redis,
    )

    async def event_gen():
        yield f"event: meta\ndata: {json.dumps({'conversation_id': conv_id})}\n\n"
        async for token in token_stream:
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


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
        model=settings.OPENROUTER_DEFAULT_MODEL,
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
        model=settings.OPENROUTER_DEFAULT_MODEL,
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
        raise HTTPException(status_code=422, detail="File must be an image")

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
