# InsightSwarm

<div align="center">

**An Autonomous Multi-Agent Academic & Market Research Engine**

[![Python](https://img.shields.io/badge/Python-55.6%25-blue?logo=python)](#tech-stack)
[![JavaScript](https://img.shields.io/badge/JavaScript-28.6%25-f7df1e?logo=javascript&logoColor=black)](#tech-stack)
[![CSS](https://img.shields.io/badge/CSS-11.3%25-1572b6?logo=css3&logoColor=white)](#tech-stack)
[![HTML](https://img.shields.io/badge/HTML-4.5%25-e34f26?logo=html5&logoColor=white)](#tech-stack)

*Turning scattered information into structured, decision-ready intelligence.*

</div>

## Highlights

- Multi-agent research orchestration with planning, retrieval, synthesis, verification, and rendering.
- PDF report generation via WeasyPrint.
- React workspace for submitting topics and viewing completed reports.
- Streamlit dashboard for tracking research activity and historical runs.
- Docker Compose setup for running the full stack locally.

## Architecture

```mermaid
flowchart LR
  U[User] --> L[Landing Page\nfrontend/landing]
  L --> R[React Workspace\nfrontend/React+Tailwind]
  R --> A[FastAPI API\napp/main.py]
  A --> G[LangGraph Research Flow\napp/graphs/research_graph.py]
  G --> T[Tavily Web Search]
  G --> M[Groq LLM]
  G --> D[(SQLite / SQLAlchemy)]
  G --> P[PDF Generation\napp/services/pdf_service.py]
  P --> F[(reports/)]
  D --> S[Streamlit Dashboard\nfrontend/streamlit/streamlit-app.py]
  F --> S
```

## What’s Inside

| Area | Purpose | Key Files |
| --- | --- | --- |
| Backend API | Receives research requests, tracks runs, exposes report downloads | [app/main.py](app/main.py), [app/api/routes.py](app/api/routes.py) |
| Research engine | Orchestrates planning, search, verification, and synthesis | [app/graphs/research_graph.py](app/graphs/research_graph.py) |
| Database layer | Async SQLAlchemy engine and sessions | [app/db/database.py](app/db/database.py) |
| PDF reports | Converts final markdown into downloadable PDFs | [app/services/pdf_service.py](app/services/pdf_service.py) |
| React workspace | Topic submission and report viewer | [frontend/React+Tailwind/src](frontend/React%2BTailwind/src) |
| Landing page | Public-facing product entry page | [frontend/landing](frontend/landing) |
| Streamlit dashboard | Activity tracker and research history viewer | [frontend/streamlit/streamlit-app.py](frontend/streamlit/streamlit-app.py) |

## Tech Stack

- Python 3.13+
- FastAPI
- LangGraph
- Groq LLM via LangChain
- Tavily search
- SQLAlchemy + SQLite
- WeasyPrint
- React 19 + React Router
- Tailwind CSS 4
- Framer Motion
- Streamlit
- Docker / Docker Compose

## Repository Layout

```text
.
├── app/                  # FastAPI backend, graph, services, database, and models
├── frontend/
│   ├── landing/          # Static marketing/entry page
│   ├── React+Tailwind/   # Research workspace UI
│   └── streamlit/        # Activity dashboard
├── devops/               # Dockerfiles and Docker Compose setup
├── reports/              # Generated PDF output
├── logs/                 # Runtime logs
├── tests/                # Test directory (currently empty)
└── pyproject.toml        # Python project metadata
```

## Prerequisites

- Python 3.13 or newer
- Node.js 18+ and npm
- `uv` for Python dependency management
- Optional: Docker Desktop and Docker Compose

## Environment Variables

Create a `.env` file in the project root. A full example is available in [`.env.example`](.env.example).

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required for the LLM used in the research graph |
| `TAVILY_API_KEY` | Required for web search retrieval |
| `LLM_MODEL` | Optional Groq model name |
| `DATABASE_URL` | Optional database connection string; defaults to SQLite |
| `REPORT_DIR` | Directory for generated PDF files |
| `TAVILY_MAX_RESULTS` | Maximum search results per query |
| `TAVILY_TOPIC` | Tavily topic setting |
| `TAVILY_SEARCH_DEPTH` | Tavily search depth |
| `LOG_LEVEL` | Logging verbosity |

Minimal example:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=sqlite+aiosqlite:///research_app.db
REPORT_DIR=reports
```

## Local Setup

### 1) Backend

Install Python dependencies and start the API:

```bash
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful backend URLs:

- API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 2) React Research Workspace

```bash
cd frontend/React+Tailwind
npm install
npm run dev
```

The workspace is designed to talk to the backend at `http://127.0.0.1:8000/api`.

### 3) Landing Page

```bash
cd frontend/landing
npm install
npm run dev
```

The landing page runs on port `3001`.

### 4) Streamlit Dashboard

```bash
uv run streamlit run frontend/streamlit/streamlit-app.py --server.port 8501 --server.address 0.0.0.0
```

The dashboard expects the backend to be available while it reads research activity and report metadata.

## Docker Setup

The full stack can be started with Docker Compose:

```bash
docker compose -f devops/docker-compose.yml up --build
```

This launches:

- Landing page on `http://localhost:3001`
- React workspace on `http://localhost:5173`
- FastAPI backend on `http://localhost:8000`
- Streamlit dashboard on `http://localhost:8501`

To stop everything:

```bash
docker compose -f devops/docker-compose.yml down
```

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/api/research` | Start a new research run |
| `GET` | `/api/research` | List research runs |
| `GET` | `/api/research/{run_id}` | Get run status |
| `GET` | `/api/research/{run_id}/report` | Fetch report metadata |
| `GET` | `/api/research/{run_id}/download` | Download or preview the PDF |

## How It Works

1. A user submits a topic in the React workspace.
2. The FastAPI backend creates a research run and starts a background LangGraph workflow.
3. The graph plans sub-questions, searches the web with Tavily, synthesizes the findings, and verifies the output.
4. The final markdown report is cleaned, stored, and rendered to PDF.
5. The React report page polls the backend until the report is ready, then displays the final document and download link.
6. The Streamlit dashboard provides a lightweight view of activity and history.

## Notes

- Generated reports and logs are persisted in `reports/` and `logs/`.
- The repository currently does not include automated tests under `tests/`.
- PDF generation uses WeasyPrint, so local environments may need the platform-specific system libraries required by that package.

## Contributing

If you extend the project, keep the README aligned with the actual run commands, ports, and environment variables. That matters here because the repository contains multiple user-facing apps in one workspace.
