# Task Planner

App for intelligent task scheduling and daily planning.
This project implements a task planner system that helps organize and prioritize tasks based on multiple parameters such as importance, interest, workload, and deadlines.

## 🧠 Features

The Task Planner is designed to help you:

- 📅 Add tasks with metadata including interest level, importance, estimated work time, and deadline.
- 🤖 Automatically calculate an optimal daily task schedule.
- ⚙️ Customize daily available time.
- 📈 Prioritize tasks using a scoring model.
- 🔐 Secure authentication and user management.
- 🏗️ Microservices architecture for scalability.

## 🚀 Motivation

I developed this app to help decide what to do each day by balancing urgency, importance, and personal interest.

---

## 🏗️ Architecture & Tech Stack

The project is structured as a set of Dockerized microservices orchestrated via Docker Compose.

*   **Language:** Python 3.12+
*   **Framework:** FastAPI (Async)
*   **Database:** PostgreSQL 16
*   **Infrastructure:** Docker, Docker Compose, Nginx (Gateway)

### Microservices

| Service | Port | Description | Path |
| :--- | :--- | :--- | :--- |
| **Gateway** | `8080` | Nginx entry point routing traffic to services. | `infra/nginx` |
| **Planner** | `8000` | Core logic for task management and scheduling. | `services/planner` |
| **Auth** | `8001` | Authentication and user management. | `services/auth` |
| **Admin** | `8002` | Administrative interfaces. | `services/admin` |

---

## 📦 Project Structure

```text
/
├── infra/                  # Infrastructure configurations (Nginx, Postgres, Fluentd)
├── services/               # Microservices source code
│   ├── admin/
│   ├── auth/
│   └── planner/
├── docker-compose.yml      # Main orchestration file
└── Makefile                # Command shortcuts
```

---

## 📥 Installation & Running

## 🛠️ Development

Before you start contributing, please read our [Contributing Guide](CONTRIBUTING.md) for coding standards and development workflows.

1. **Clone the repo**
   ```bash
   git clone <repo_url>
   cd task-planner-app
   ```

2. **Run with Docker Compose**
   The easiest way to start the application is using the provided Makefile.

   ```bash
   make dev
   ```
   This will start all services in development mode.

3. **Other Commands**
   *   **Stop Environment:** `make down`
   *   **Rebuild:** `make build`
   *   **Database Shell:** `make db-shell`

---

## 📝 Usage

Once the application is running, you can access the services via the API Gateway (Nginx) on port `8080` or directly on their respective ports for debugging.

*   **Auth Service:** `http://localhost:8001`
*   **Planner Service:** `http://localhost:8000`
*   **Admin Service:** `http://localhost:8002`

Swagger documentation should be available at `/docs` for each service (e.g., `http://localhost:8000/docs`).

---

## 📌 Contributing

Before contributing, please read our [Contributing Guide](CONTRIBUTING.md) for coding standards and branch naming conventions.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your fork and open a Pull Request

### Repository Management

- [Branch Protection Rules](docs/branch-protection.md) — How we protect `main` and other branches
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development workflow