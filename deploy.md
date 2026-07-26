# Deployment Guide

This document outlines a free-tier deployment plan for the InsightSwarm project.

## Recommended free deployment architecture

Use the following services:

- Backend API: Render
- Frontend: Cloudflare Pages or Vercel
- Database: Neon (Postgres)
- Landing page: Cloudflare Pages or Vercel
- Streamlit dashboard: optional, best kept local or removed from the free deployment plan

This is the most practical free setup because the current project is built around a FastAPI backend plus React frontend, not a Docker-only deployment.

## Why this approach

The repository already contains:

- a FastAPI backend in [app/main.py](app/main.py)
- a React/Vite frontend in [frontend/React+Tailwind](frontend/React+Tailwind)
- a landing page in [frontend/landing](frontend/landing)
- a Docker-based local setup in [devops/docker-compose.yml](devops/docker-compose.yml)

Free-tier hosting works best when we avoid Docker and keep the deployment focused on the backend and frontend.

## Deployment steps

### 1. Prepare the repository

1. Push the project to GitHub.
2. Make sure environment variables are documented and available.
3. Ensure the backend can start with a production-friendly host/port configuration.

### 2. Deploy the backend on Render

Create a new Render web service from the repository.

#### Suggested settings

- Runtime: Python
- Build command:

```bash
pip install uv
uv sync
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Required environment variables

Add these in Render:

- `GROQ_API_KEY`
- `TAVILY_API_KEY`
- `DATABASE_URL`
- `REPORT_DIR`
- `LOG_LEVEL`

Optional:

- `LLM_MODEL`
- `TAVILY_MAX_RESULTS`
- `TAVILY_TOPIC`
- `TAVILY_SEARCH_DEPTH`

### 3. Use a free Postgres database

Use Neon or another free Postgres provider.

Set the connection string in Render as:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>
```

This is recommended because the current stack is easier to run reliably with Postgres instead of local SQLite assumptions.

### 4. Deploy the frontend on Cloudflare Pages or Vercel

Deploy the React app in [frontend/React+Tailwind](frontend/React+Tailwind).

#### Frontend environment variables

Set the API base URL:

```env
VITE_API_URL=https://your-backend-url.onrender.com
```

If the frontend is using the landing page separately, deploy that too with its own URL.

### 5. Update CORS on the backend

The backend in [app/main.py](app/main.py) should allow the deployed frontend origin.

Add the deployed frontend URL to the allowed origins list.

### 6. Test the deployment

After deployment:

1. Visit the backend health endpoint:

```text
https://your-backend-url.onrender.com/health
```

2. Confirm the frontend loads without API errors.
3. Submit a sample research request.
4. Verify that the report generation and download flow works.

## Limitations of free-tier hosting

Free hosting is suitable for demos and student projects, but it has real constraints:

- apps may sleep when idle
- cold starts can be slow
- background jobs may be interrupted
- file persistence for generated PDFs is less reliable than paid hosting
- API rate limits may affect research requests

## Recommended scope for the first deployment

For the first public deployment, keep the scope focused on:

- backend API
- frontend submission/report UI
- basic report generation

Skip the Streamlit dashboard for the initial free deployment unless you have a separate hosting option for it.

## Suggested milestone plan

### Milestone 1

- Deploy backend successfully
- Confirm `/health` works

### Milestone 2

- Deploy frontend successfully
- Connect frontend to backend

### Milestone 3

- Test end-to-end research submission
- Confirm report generation and download

## Notes

If you want a more robust future deployment, the next step would be to move the research workflow to a worker-based setup and use cloud storage for generated reports.
