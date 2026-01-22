# Best Practices & Development Rules — Task Planner

## 1. General Principles
*   **Microservices Approach**: Each service (`auth`, `planner`, `admin`) is autonomous, maintains its own DB (or schema), and manages dependencies via Poetry.
*   **Asynchrony**: All I/O (database, external requests, Redis) must be asynchronous (`async/await`).
*   **Static Typing**: Mandatory use of Type Hints for all function arguments and return values.

## 2. Code Style and Linting
*   **Tooling**: **Ruff** is used for linting and formatting.
*   **Automation**: It is recommended to run `make lint` before committing.
*   **Standards**: Follow PEP 8, but rely on Ruff configurations in `pyproject.toml`.

## 3. Service Architecture
Each service in `services/` must adhere to the following structure:
*   `src/api/`: FastAPI endpoints, separated by logical modules.
*   `src/core/`: Configuration (`config.py`), security, database connection.
*   `src/crud/`: Database interaction logic (separated from API).
*   `src/models/`: SQLAlchemy models.
*   `src/schemas/`: Pydantic schemas for input and output data validation.

## 4. Database Interaction
*   **SQLAlchemy 2.0**: Use modern syntax: `Mapped` and `mapped_column`.
*   **Migrations**: Any database structure change must be accompanied by an Alembic migration.
    *   Generate: `alembic revision --autogenerate -m "description"`.
    *   Apply: `make alembic-upgrade`.
*   **Relationships**: Use `TYPE_CHECKING` in models to prevent circular imports when defining `relationship`.

## 5. Validation and Schemas
*   **Pydantic**: Use Pydantic v2.
*   **BaseSchema**: Inherit from `BaseSchema` (in `core/config.py`), which includes `from_attributes = True` for convenient conversion of SQLAlchemy models to DTOs.
*   **Configuration**: Settings are stored in `src/core/config.py` using `pydantic-settings`. Secrets are loaded from `.env`.

## 6. Testing
*   **Framework**: `pytest` with `pytest-asyncio` plugin.
*   **Isolation**: Use a separate environment variables file `.test.env` for tests.
*   **Location**: Tests are located in the `tests/` folder of each service, divided into `unit_tests` and `integration_tests`.
*   **Execution**: `make test`.

## 7. Docker and CI/CD
*   **Makefile**: Use the `Makefile` in the project root as a single entry point for commands (`make dev`, `make build`, `make test`, `make lint`).
*   **Containerization**: Each service has its own `Dockerfile`. General orchestration is handled via `docker-compose.yml`.
*   **Logging**: Infrastructure includes Fluentd and Elasticsearch for log collection (see `docker-compose.logging.yaml`).

## 8. Git Workflow
*   **Commit Messages**: Concise, in the present tense, reflecting the essence of the changes.
*   **Dependencies**: When adding libraries, update `poetry.lock` inside the container or via local poetry.