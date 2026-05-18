import datetime as dt
import json
import logging
from typing import Any

import httpx
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import delete_cache_by_prefix
from src.core.config import settings
from src.crud import allocation_crud, calendar_crud, day_crud, task_crud
from src.models import AIConversation, AIMessage, Allocation, Calendar
from src.models.allocation import AllocationType
from src.schemas import task as task_schemas
from src.schemas.allocation import AllocationCreateSchema, AllocationSchema, AllocationUpdateSchema
from src.schemas.calendar import CalendarCreateSchema, CalendarSchema, CalendarUpdateSchema
from src.schemas.day import DaySchema, DayUpdateSchema

logger = logging.getLogger("ai")

AI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task for the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "deadline": {"type": ["string", "null"], "description": "YYYY-MM-DD or null"},
                    "interest": {"type": ["integer", "null"], "minimum": 1, "maximum": 10},
                    "importance": {"type": ["integer", "null"], "minimum": 1, "maximum": 10},
                    "work_hours": {"type": ["integer", "null"], "minimum": 1, "maximum": 24},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task that belongs to the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "name": {"type": ["string", "null"]},
                    "deadline": {"type": ["string", "null"]},
                    "interest": {"type": ["integer", "null"], "minimum": 1, "maximum": 10},
                    "importance": {"type": ["integer", "null"], "minimum": 1, "maximum": 10},
                    "work_hours": {"type": ["integer", "null"], "minimum": 1, "maximum": 24},
                    "tags": {"type": ["array", "null"], "items": {"type": "string"}},
                },
                "required": ["task_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar",
            "description": "Create a calendar for the current user",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_calendar",
            "description": "Update an existing calendar that belongs to the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "integer"},
                    "name": {"type": "string"},
                },
                "required": ["calendar_id", "name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_allocation",
            "description": "Create an allocation in a calendar owned by the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["even", "priority", "compact"]},
                    "day_limits": {"type": ["object", "null"]},
                },
                "required": ["calendar_id", "name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_allocation",
            "description": "Update an existing allocation that belongs to the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "allocation_id": {"type": "integer"},
                    "name": {"type": ["string", "null"]},
                    "type": {"type": ["string", "null"], "enum": ["even", "priority", "compact", None]},
                    "day_limits": {"type": ["object", "null"]},
                },
                "required": ["allocation_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_day",
            "description": "Update a day in a calendar that belongs to the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "day_id": {"type": "integer"},
                    "work_hours": {"type": ["integer", "null"], "minimum": 0, "maximum": 24},
                },
                "required": ["day_id", "work_hours"],
                "additionalProperties": False,
            },
        },
    },
]


async def build_system_prompt(user_id: int, session: AsyncSession) -> str:
    tasks_result = await task_crud.schema_owner_list(session, owner_id=user_id)
    alloc_stmt = (
        select(Allocation)
        .join(Calendar, Allocation.calendar_id == Calendar.id)
        .where(Calendar.user_id == user_id)
    )
    allocations_result = list((await session.scalars(alloc_stmt)).all())

    tasks_text = "No tasks yet." if not tasks_result else "\n".join([
        f"- {t.name} (interest={t.interest}, importance={t.importance}, "
        f"work_hours={t.work_hours}, deadline={t.deadline})"
        for t in tasks_result
    ])

    allocations_text = "No allocations yet." if not allocations_result else "\n".join([
        f"- {a.name} (type={a.type}, limits={a.day_limits})"
        for a in allocations_result
    ])

    return f"""You are a helpful AI assistant for a task planner application.
The user has the following tasks:
{tasks_text}

The user has the following allocations:
{allocations_text}

You help users manage their tasks, calendars, allocations and days.
When user asks to change data, use tool calls.
Never ask for owner_id/user_id and never invent IDs.
Be concise and helpful."""


async def call_openrouter(
    messages: list[dict[str, Any]],
    model: str = settings.OPENROUTER_DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | None = None,
) -> dict[str, Any]:
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider is not configured",
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Task Planner AI",
    }
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools
    if tool_choice:
        payload["tool_choice"] = tool_choice

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(settings.OPENROUTER_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error("OpenRouter error: %s - %s", response.status_code, response.text)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider request failed",
        )
    return response.json()


def extract_json_payload(content: str) -> dict[str, Any]:
    clean = content
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0]
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0]
    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"AI response is not valid JSON: {e}",
        ) from e


def _loads_tool_args(raw_args: str) -> dict[str, Any]:
    try:
        return json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tool arguments are not valid JSON: {exc}",
        ) from exc


async def _invalidate_planner_cache(redis: Redis | None, user_id: int) -> None:
    if redis is None:
        return
    await delete_cache_by_prefix(redis, f"planner:calendar:{user_id}")
    await delete_cache_by_prefix(redis, f"planner:calendar_with_tasks:{user_id}")


async def _get_or_create_conversation(
    session: AsyncSession,
    user_id: int,
    conversation_id: int | None,
) -> AIConversation:
    if conversation_id is None:
        conversation = AIConversation(user_id=user_id)
        session.add(conversation)
        await session.flush()
        await session.refresh(conversation)
        return conversation

    stmt = select(AIConversation).where(
        AIConversation.id == conversation_id,
        AIConversation.user_id == user_id,
    )
    conversation = await session.scalar(stmt)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


async def _store_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    tool_name: str | None = None,
    tool_call_id: str | None = None,
) -> None:
    msg = AIMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_call_id=tool_call_id,
    )
    session.add(msg)
    conversation = await session.get(AIConversation, conversation_id)
    if conversation is not None:
        conversation.updated_at = dt.datetime.utcnow()
    await session.flush()


async def _load_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 30,
) -> list[dict[str, Any]]:
    stmt = (
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.id.desc())
        .limit(limit)
    )
    rows = list((await session.scalars(stmt)).all())
    rows.reverse()

    history: list[dict[str, Any]] = []
    for msg in rows:
        if msg.role == "tool":
            history.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id or "",
                    "name": msg.tool_name or "",
                    "content": msg.content,
                }
            )
            continue
        history.append({"role": msg.role, "content": msg.content})
    return history


async def execute_tool_call(
    user_id: int,
    session: AsyncSession,
    redis: Redis | None,
    tool_name: str,
    raw_args: str,
) -> dict[str, Any]:
    args = _loads_tool_args(raw_args)

    if tool_name == "create_task":
        schema = task_schemas.CreateTaskSchema(
            name=args["name"][:128],
            deadline=args.get("deadline"),
            interest=args.get("interest"),
            importance=args.get("importance"),
            work_hours=args.get("work_hours"),
            tags=args.get("tags", []),
            is_ai_created=True,
        )
        task = await task_crud.schema_owner_create(session, schema, user_id)
        await session.commit()
        await _invalidate_planner_cache(redis, user_id)
        return {"task": task.model_dump()}

    if tool_name == "update_task":
        task_id = int(args["task_id"])
        task_obj = await task_crud.schema_owner_get(session, task_id, user_id)
        update_schema = task_schemas.UpdateTaskSchema(
            name=args.get("name"),
            deadline=args.get("deadline"),
            interest=args.get("interest"),
            importance=args.get("importance"),
            work_hours=args.get("work_hours"),
            tags=args.get("tags"),
        )
        updated_task = await task_crud.schema_update_by_id(session, task_obj.id, update_schema)
        await session.commit()
        await _invalidate_planner_cache(redis, user_id)
        return {"task": updated_task.model_dump()}

    if tool_name == "create_calendar":
        schema = CalendarCreateSchema(name=args["name"][:128])
        calendar = await calendar_crud.schema_owner_create(session, schema, user_id)
        await session.commit()
        return {"calendar": CalendarSchema.model_validate(calendar).model_dump()}

    if tool_name == "update_calendar":
        calendar_id = int(args["calendar_id"])
        await calendar_crud.schema_owner_get(session, calendar_id, user_id)
        schema = CalendarUpdateSchema(name=args["name"][:128])
        updated_calendar = await calendar_crud.schema_update_by_id(session, calendar_id, schema)
        await session.commit()
        return {"calendar": CalendarSchema.model_validate(updated_calendar).model_dump()}

    if tool_name == "create_allocation":
        calendar_id = int(args["calendar_id"])
        calendar = await calendar_crud.get(session, calendar_id)
        if calendar is None or calendar.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

        alloc_schema = AllocationCreateSchema(
            name=args["name"][:128],
            type=AllocationType(args.get("type", "even")),
            day_limits=args.get("day_limits"),
        )
        created_alloc = await allocation_crud.create_for_calendar(session, calendar_id, alloc_schema)
        await session.commit()
        await _invalidate_planner_cache(redis, user_id)
        return {"allocation": AllocationSchema.model_validate(created_alloc).model_dump()}

    if tool_name == "update_allocation":
        allocation_id = int(args["allocation_id"])
        await allocation_crud.get_or_raise(session, allocation_id, user_id)

        alloc_type = args.get("type")
        update_schema = AllocationUpdateSchema(
            name=args.get("name"),
            type=AllocationType(alloc_type) if alloc_type is not None else None,
            day_limits=args.get("day_limits"),
        )
        updated_alloc = await allocation_crud.update_by_id(session, allocation_id, update_schema)
        await session.commit()
        await _invalidate_planner_cache(redis, user_id)
        return {"allocation": AllocationSchema.model_validate(updated_alloc).model_dump()}

    if tool_name == "update_day":
        day_id = int(args["day_id"])
        day = await day_crud.schema_owner_get_by_id(session, day_id, user_id)
        update_schema = DayUpdateSchema(work_hours=args.get("work_hours"))
        day_obj = await day_crud.get(session, day.id)
        updated_day = await day_crud.update(
            session,
            day_obj,
            **update_schema.model_dump(exclude_unset=True),
        )
        await session.commit()
        await _invalidate_planner_cache(redis, user_id)
        return {"day": DaySchema.model_validate(updated_day).model_dump()}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown tool: {tool_name}")


async def run_chat_with_tools(
    user_id: int,
    message: str,
    session: AsyncSession,
    model: str,
    llm_call: Any,
    redis: Redis | None = None,
    conversation_id: int | None = None,
) -> dict[str, Any]:
    conversation = await _get_or_create_conversation(session, user_id, conversation_id)
    system_prompt = await build_system_prompt(user_id, session)
    history = await _load_conversation_history(session, conversation.id)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        *history,
    ]
    await _store_message(session, conversation.id, "user", message)
    messages.append({"role": "user", "content": message})

    for _ in range(6):
        result = await llm_call(
            messages,
            model=model,
            temperature=0.4,
            tools=AI_TOOLS,
            tool_choice="auto",
        )
        assistant_message = result["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls") or []

        if not tool_calls:
            await _store_message(
                session,
                conversation.id,
                "assistant",
                assistant_message.get("content", ""),
            )
            await session.commit()
            return {
                "response": assistant_message.get("content", ""),
                "model": result.get("model", model),
                "usage": result.get("usage", {}),
                "conversation_id": conversation.id,
            }

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.get("content") or "",
                "tool_calls": tool_calls,
            }
        )
        await _store_message(
            session,
            conversation.id,
            "assistant",
            assistant_message.get("content") or "",
        )

        for call in tool_calls:
            function_data = call.get("function", {})
            tool_name = function_data.get("name", "")
            raw_args = function_data.get("arguments", "{}")

            try:
                tool_result = await execute_tool_call(user_id, session, redis, tool_name, raw_args)
            except HTTPException as exc:
                tool_result = {"error": exc.detail}
            except Exception as exc:  # pragma: no cover
                logger.exception("Unexpected tool execution error")
                tool_result = {"error": str(exc)}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "name": tool_name,
                    "content": json.dumps(tool_result, default=str),
                }
            )
            await _store_message(
                session,
                conversation.id,
                "tool",
                json.dumps(tool_result, default=str),
                tool_name=tool_name,
                tool_call_id=call.get("id"),
            )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="AI exceeded maximum tool-calling steps",
    )


async def create_task_via_ai(
    user_id: int,
    instruction: str,
    session: AsyncSession,
    model: str,
    llm_call: Any,
) -> task_schemas.TaskSchema:
    existing_tasks = await task_crud.schema_owner_list(session, owner_id=user_id)
    tasks_context = "\n".join([
        f"- {t.name} (interest={t.interest}, importance={t.importance}, "
        f"work_hours={t.work_hours})"
        for t in existing_tasks
    ]) if existing_tasks else "No existing tasks."

    system_prompt = f"""You are a task creation assistant. Based on the user's instruction, extract task parameters.
Return ONLY a valid JSON object with these fields:
- name (string, max 128 chars): task name
- interest (int, 1-10): interest level
- importance (int, 1-10): importance level
- work_hours (int, 1-24): estimated work hours
- deadline (string or null): ISO date format YYYY-MM-DD, or null if not specified
- tags (array of strings): relevant tags

Example of existing tasks for reference:
{tasks_context}

Return valid JSON only, no additional text."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Create a task: {instruction}"},
    ]
    result = await llm_call(messages, model=model, temperature=0.5)
    task_data = extract_json_payload(result["choices"][0]["message"]["content"])

    task_schema = task_schemas.CreateTaskSchema(
        name=task_data["name"][:128],
        interest=task_data.get("interest"),
        importance=task_data.get("importance"),
        work_hours=task_data.get("work_hours"),
        deadline=task_data.get("deadline"),
        tags=task_data.get("tags", []),
        is_ai_created=True,
    )
    created_task = await task_crud.schema_owner_create(session, task_schema, user_id)
    await session.commit()
    return created_task


async def create_allocation_via_ai(
    user_id: int,
    calendar_id: int,
    instruction: str,
    session: AsyncSession,
    model: str,
    llm_call: Any,
) -> AllocationSchema:
    calendar = await calendar_crud.get(session, calendar_id)
    if calendar is None or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

    system_prompt = (
        "You are an allocation creation assistant. "
        "Based on the user's instruction, extract allocation parameters. "
        "Return ONLY a valid JSON object with these fields:\n"
        '- name (string, max 128 chars): allocation name\n'
        '- type (string): ONE of "even", "priority", "compact"\n'
        '- day_limits (object or null): e.g. {"monday": 4, "wednesday": 6} or null\n'
        "Return valid JSON only, no additional text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Create an allocation: {instruction}"},
    ]
    result = await llm_call(messages, model=model, temperature=0.5)
    alloc_data = extract_json_payload(result["choices"][0]["message"]["content"])

    alloc_schema = AllocationCreateSchema(
        name=alloc_data["name"][:128],
        type=AllocationType(alloc_data.get("type", "even")),
        day_limits=alloc_data.get("day_limits"),
    )
    created_alloc = await allocation_crud.create_for_calendar(session, calendar_id, alloc_schema)
    await session.commit()
    return AllocationSchema.model_validate(created_alloc)
