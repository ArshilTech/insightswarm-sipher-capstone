# DevOps Setup Guide

This folder contains the Docker configuration for running the InsightSwarm project.

## Services

- FastAPI Backend (Port 8000)
- React Frontend (Port 5173)

## Prerequisites

- Docker Desktop
- Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

## Environment Variables

Create a `.env` file in the project root.

Required variables:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Running the Project

From the project root:

```bash
docker compose -f devops/docker-compose.yml up --build
```

For subsequent runs:

```bash
docker compose -f devops/docker-compose.yml up
```

## Access the Application

Frontend:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

## Stopping Containers

```bash
docker compose -f devops/docker-compose.yml down
```

## Rebuilding Containers

```bash
docker compose -f devops/docker-compose.yml build --no-cache
```

## Notes

- Backend uses FastAPI and Uvicorn.
- Frontend uses React + Vite.
- Docker image includes Linux dependencies required by WeasyPrint for PDF generation.
- Database tables are initialized automatically during backend startup.