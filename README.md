# Task Planner

Intelligent task scheduling and daily planning application with AI-powered insights and dark theme interface.

## Overview

Task Planner helps you organize and prioritize tasks based on importance, interest, workload, and deadlines. The application features an intelligent AI agent that provides scheduling insights and helps optimize your daily workflow.

---

## Features

- **Task Management**: Add tasks with interest level, importance, estimated work time, and deadlines
- **AI Agent**: Get intelligent scheduling recommendations and workload analysis
- **Smart Scheduling**: Automatic daily task allocation using multiple allocation methods
- **Dark Theme**: Modern dark UI with OKLCH color palette for comfortable viewing
- **Real-time Sync**: Instant synchronization across all connected clients
- **Calendar Views**: Day, week, and month calendar views with drag-and-drop
- **Secure Authentication**: JWT-based authentication with role support
- **Microservices Architecture**: Scalable backend with FastAPI microservices

---

## Screenshots

| Light Theme | Dark Theme |
|-------------|------------|
| ![Tasks - Light](./docs/screenshots/tasks-light.png) | ![Tasks - Dark](./docs/screenshots/tasks-dark.png) |
| ![Schedule - Light](./docs/screenshots/schedule-light.png) | ![Schedule - Dark](./docs/screenshots/schedule-dark.png) |
| ![AI Assistant - Light](./docs/screenshots/ai-assistant-light.png) | ![AI Assistant - Dark](./docs/screenshots/ai-assistant-dark.png) |

---

## Architecture

The project uses a microservices architecture with Docker Compose orchestration.

```
task-planner-app/
├── infra/                     # Docker configs, nginx, postgres
├── services/                  # Backend microservices
│   ├── admin/                 # Admin service (port 8002)
│   ├── auth/                  # Auth service (port 8001)
│   └── planner/               # Planner service (port 8000)
├── frontend/                  # Vue 3 frontend
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── assets/           # CSS, fonts, images
│   │   ├── components/        # Vue components
│   │   │   └── ui/           # Shadcn-vue UI components
│   │   ├── composables/       # Vue composables
│   │   ├── guards/            # Route guards
│   │   ├── i18n/             # Internationalization
│   │   ├── layouts/          # App layouts
│   │   ├── lib/              # Utility libraries
│   │   ├── locales/          # Translation files
│   │   ├── router/           # Vue Router
│   │   ├── stores/           # Pinia stores
│   │   ├── types/            # TypeScript types
│   │   └── views/            # Page views
│   ├── e2e/                   # Playwright E2E tests
│   └── public/               # Static assets
├── docker-compose*.yml        # Compose orchestrator
├── Makefile                  # Dev commands
└── README.md
```

---

## Tech Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL 16
- **Cache**: Redis
- **Infrastructure**: Docker, Docker Compose, Nginx

### Frontend
- **Framework**: Vue 3 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 (CSS-first configuration)
- **State Management**: Pinia with real-time sync
- **UI Components**: Shadcn-vue + Reka UI
- **Testing**: Vitest (unit) + Playwright (E2E)

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.12+ (for local backend development)

### Start All Services

```bash
make dev
```

This starts:
- **Frontend**: http://localhost:5173
- **Gateway**: http://localhost:8081
- **Planner API**: http://localhost:8000
- **Auth API**: http://localhost:8001
- **Admin API**: http://localhost:8002

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Type check
npm run type-check

# Build for production
npm run build

# Run unit tests
npm run test:run

# Run E2E tests (requires backend running)
npm run test:e2e
```

### Backend Commands

```bash
# Start all services
make dev

# Stop all services
make down

# Rebuild images
make build

# Run backend tests
make test

# Lint backend
make lint

# Access database shell
make db-shell
```

---

## Design System

### Dark Theme (Default)

The application uses a sophisticated dark theme with OKLCH colors for optimal visual comfort:

| Token | OKLCH | Hex | Usage |
|-------|-------|-----|-------|
| Background | `oklch(0.145 0 0)` | `#0e0e0c` | Page background |
| Surface | `oklch(0.188 0.005 285)` | `#2a2b2a` | Cards, panels |
| Surface Elevated | `oklch(0.255 0.005 285)` | `#3c3d3c` | Hover states |
| Primary | `oklch(0.65 0.17 25)` | `#c26d51` | Primary actions |
| Accent | `oklch(0.70 0.15 240)` | `#6799cc` | Links, highlights |
| Border | `oklch(0.26 0.005 285)` | `#3d3e3d` | Borders, dividers |
| Text Primary | `oklch(0.92 0.005 285)` | `#e6e6e5` | Main text |
| Text Muted | `oklch(0.65 0.005 285)` | `#989997` | Secondary text |

### Typography
- **Display**: Cormorant Garamond (serif) - headings
- **Body**: Inter (sans-serif) - body text

### Key Files
- `frontend/src/assets/main.css` - Design tokens (`@theme` variables)
- `frontend/src/assets/dark.css` - Dark theme overrides
- `frontend/components.json` - Shadcn-vue configuration

---

## Testing

### Backend Tests
```bash
# Run all backend tests
make test

# Run specific service tests
docker compose run --rm planner uv run pytest -v
```

### Frontend Unit Tests (Vitest)
```bash
cd frontend
npm run test        # Watch mode
npm run test:run    # Single run
```

### Frontend E2E Tests (Playwright)
```bash
cd frontend

# Install browsers (first time)
npx playwright install chromium

# Run E2E tests
npm run test:e2e
```

---

## API Documentation

Once running, access Swagger documentation:

| Service | URL |
|---------|-----|
| Planner | http://localhost:8000/docs |
| Auth | http://localhost:8001/docs |
| Admin | http://localhost:8002/docs |

---

## Configuration

### Backend Environment Variables

Create `.env` files in each service directory:

**services/planner/.env**
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/planner
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-here
```

**services/auth/.env**
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@5432/auth
SECRET_KEY=your-secret-key-here
```

### Frontend Environment Variables

**frontend/.env**
```
VITE_API_URL=http://localhost:8081
```

---

## Contributing

Before contributing, please read:
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow and code standards
- [CODE_STYLE.md](CODE_STYLE.md) - Detailed code style guidelines

### Branch Naming
```
feat/task-description     # New features
fix/bug-description       # Bug fixes
refactor/description      # Refactoring
docs/description          # Documentation
test/description          # Tests
style/description         # Styling
```

### Commit Message Format
```
type(scope): description

Types: feat, fix, refactor, docs, test, style, chore
Scope: frontend, backend, api, auth, planner, etc.
```

Examples:
```
feat(frontend): add dark mode toggle
fix(planner): resolve calendar allocation bug
docs(auth): update JWT token documentation
```

---

## Security

- JWT tokens for authentication
- Tokens stored in localStorage (frontend) and Redis (backend)
- HTTP-only cookies recommended for production
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM

---

## License

[Your License Here]
