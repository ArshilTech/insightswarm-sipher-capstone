# DevOps Setup Guide

This folder contains the Docker configuration for running the complete InsightSwarm project using Docker Compose.

## Project Architecture

```text
Landing Page (Vite)       -> Port 3001
React Workspace (Vite)    -> Port 5173
FastAPI Backend           -> Port 8000
Streamlit Dashboard       -> Port 8501
```

## Services

The Docker Compose setup includes:

- Landing Page (Port 3001)
- React Workspace (Port 5173)
- FastAPI Backend (Port 8000)
- Streamlit Dashboard (Port 8501)

## Prerequisites

Install the following before running the project:

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

## Docker Files

```text
devops/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.landing
├── Dockerfile.streamlit
└── README_DEVOPS.md
```

## Running the Project

From the project root directory:

```bash
docker compose -f devops/docker-compose.yml up --build
```

This command will:

- Build all Docker images
- Start all containers
- Create the required Docker network
- Expose all application ports

## Subsequent Runs

After the initial build:

```bash
docker compose -f devops/docker-compose.yml up
```

## Access the Application

### Landing Page

```text
http://localhost:3001
```

### React Workspace

```text
http://localhost:5173
```

### FastAPI Backend

```text
http://localhost:8000
```

### Swagger Documentation

```text
http://localhost:8000/docs
```

### Streamlit Dashboard

```text
http://localhost:8501
```

## Stopping the Project

```bash
docker compose -f devops/docker-compose.yml down
```

## Rebuilding Images

If dependencies or Dockerfiles change:

```bash
docker compose -f devops/docker-compose.yml up --build
```

To force a clean rebuild:

```bash
docker compose -f devops/docker-compose.yml build --no-cache
```

## Viewing Running Containers

```bash
docker ps
```

## Viewing Logs

All services:

```bash
docker compose -f devops/docker-compose.yml logs -f
```

Specific service:

```bash
docker compose -f devops/docker-compose.yml logs -f backend
```

Examples:

```bash
docker compose -f devops/docker-compose.yml logs -f frontend
docker compose -f devops/docker-compose.yml logs -f landing
docker compose -f devops/docker-compose.yml logs -f streamlit
```

## Troubleshooting

### Port Already in Use

If a port is occupied by another application, stop the conflicting process or update the port mapping in `docker-compose.yml`.

### Docker Desktop Not Running

Ensure Docker Desktop is started before executing any Docker commands.

### Environment Variable Errors

Verify that:

```env
GROQ_API_KEY
TAVILY_API_KEY
```

are correctly configured inside the root `.env` file.

### Backend Fails During PDF Generation

The backend image includes the required Linux dependencies for WeasyPrint PDF generation.

Rebuild the backend image if dependency-related issues occur:

```bash
docker compose -f devops/docker-compose.yml build backend --no-cache
```

## Development Notes

- Backend uses FastAPI with Uvicorn.
- Frontend Workspace uses React + Vite.
- Landing Page is a separate Vite application.
- Streamlit Dashboard runs independently on port 8501.
- Docker Compose orchestrates all services through a shared Docker network.
- Environment variables are loaded from the root `.env` file.
- Database initialization occurs automatically during backend startup.

## Verification Checklist

After starting the containers:

- [ ] Landing Page loads on port 3001
- [ ] React Workspace loads on port 5173
- [ ] FastAPI backend responds on port 8000
- [ ] Swagger UI opens on `/docs`
- [ ] Streamlit Dashboard loads on port 8501
- [ ] Research workflow executes successfully
- [ ] PDF generation works correctly

## Team Usage

Any team member can run the project by:

1. Cloning the repository
2. Creating a valid `.env` file
3. Starting Docker Desktop
4. Running:

```bash
docker compose -f devops/docker-compose.yml up --build
```

No manual installation of Python packages, Node.js dependencies, Streamlit packages, or system libraries is required.