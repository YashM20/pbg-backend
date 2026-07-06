# PBG Backend

FastAPI backend service for processing, extracting, and comparing documents.

## Project Structure

```text
├── app/
│   ├── core/               # Application configuration and DB pool setup
│   │   ├── config.py       # Pydantic configuration settings loaded from environment
│   │   └── db.py           # asyncpg connection pool initialization and helpers
│   ├── modules/            # API feature modules
│   │   ├── documents/      # Document management endpoints
│   │   ├── extraction/     # Data extraction endpoints
│   │   ├── comparison/     # Document comparison logic
│   │   ├── jobs/           # Background/asynchronous job management
│   │   └── health/         # System status and DB connectivity check
│   ├── main.py             # FastAPI server initialization and router mounting
│   └── worker.py           # Background task worker (if applicable)
├── migrations/             # Database migrations (Alembic/SQL scripts)
├── Dockerfile              # Docker multi-stage build configuration
├── docker-compose.yml      # Local development Docker setup (api + postgres db)
├── makefile                # Shell shortcuts (make dev)
├── pyproject.toml          # Project metadata and dependencies (managed by uv)
└── uv.lock                 # Pinned dependencies lock file
```

---

## Getting Started

### Prerequisites
- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** package manager (recommended for fast installation)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pbg-backend
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://neondb_owner:password@host/neondb?sslmode=require
ENV=dev
```

### 3. Setup Virtual Environment & Install Dependencies
Using `uv`, you can synchronize the dependencies defined in `pyproject.toml` and lockfile directly:
```bash
# Create venv and install dependencies
uv sync
```

---

## Running the Application

### Development Server (Local Host)
To run the server locally with auto-reload:
```bash
make dev
```
The server will start at `http://127.0.0.1:8000`.
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Running with Docker Compose
To build and start both the API and a local PostgreSQL database container:
```bash
docker-compose up --build
```
This mounts the DB on port `5432` and the API on port `8000`.

---

## Development Utilities

### Dependency Management (with `uv`)
- Add a new dependency:
  ```bash
  uv add <package-name>
  ```
- Add a development-only dependency:
  ```bash
  uv add --dev <package-name>
  ```
- Install all defined packages:
  ```bash
  uv sync
  ```

### Linting and Formatting
Check the code formatting using Ruff:
```bash
uv run ruff check .
```

### Running Tests
To execute unit tests:
```bash
uv run pytest
```

---

## API Endpoints Overview

| Route | Tag | Description |
|---|---|---|
| `GET /health` | `health` | System status check & database connectivity health probe |
| `/documents` | `documents` | Operations on documents (uploading, listing) |
| `/extraction` | `extraction` | Document text and metadata extraction endpoints |
| `/comparison` | `comparison` | Document structure and text comparison endpoints |
| `/jobs` | `jobs` | Background tasks tracking and status |