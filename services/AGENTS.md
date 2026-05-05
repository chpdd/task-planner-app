# Services - Microservices Module

## OVERVIEW

Three FastAPI microservices sharing PostgreSQL + Redis infrastructure.

## STRUCTURE

```
services/
├── planner/           # Task scheduling & calendar (port 8000)
│   └── src/
│       ├── api/       # routers: task.py, planner.py, manual_day.py, logger_check.py
│       ├── models/    # User, Task, Day, TaskExecution, FailedTask, ManualDay
│       ├── schemas/   # Pydantic DTOs
│       ├── crud/      # Database operations
│       └── core/      # config, security, database, cache, middleware, log
├── auth/              # Authentication (port 8001)
│   └── src/
│       ├── api/       # routers: auth.py, user.py
│       ├── models/    # User
│       ├── schemas/   # Pydantic DTOs
│       ├── crud/
│       └── core/      # config, security, database (NO redis)
└── admin/             # Database maintenance (port 8002)
    └── src/
        ├── api/       # router: admin.py (VACUUM, REINDEX)
        ├── models/    # Mirror of planner models
        ├── schemas/
        ├── crud/
        └── core/      # config, database (NO redis)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add task endpoint | `planner/src/api/task.py` | POST /tasks |
| Scheduling logic | `planner/src/api/planner.py` | GET /calendar, POST /allocate |
| Allocation algorithms | `planner/src/crud/planner.py` | 5 methods |
| Auth endpoints | `auth/src/api/auth.py` | POST /register, /login, /refresh |
| DB maintenance | `admin/src/api/admin.py` | VACUUM, REINDEX |
| Redis cache | `planner/src/core/cache.py` | Calendar caching |

## CONVENTIONS

- **API directory name**: `api/` not `routers/`
- **No service layer**: Routers call crud directly
- **Shared DB**: All services connect to same PostgreSQL
- **User model duplication**: User model in each service
- **Tests**: `tests/integration_tests/` + `tests/unit_tests/`

## ANTI-PATTERNS

- **Duplicate security.py**: Copied in planner + auth (not shared)
- **Duplicate User model**: Exists in all 3 services
- **Missing integration_tests**: auth/admin have only unit_tests
- **No lifespan**: auth/admin missing Redis lifecycle handlers

## COMMANDS

```bash
# Service-specific
docker compose run --rm planner poetry run pytest -v
docker compose run --rm auth poetry run pytest -v
docker compose run --rm admin poetry run pytest -v

# Service-specific lint
docker compose run --rm planner poetry run ruff check .
```
