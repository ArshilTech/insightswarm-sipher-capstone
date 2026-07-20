# DevOps Workspace

<<<<<<< HEAD
This folder contains Docker and database configuration placeholders for the project.
=======
This folder contains the Docker configuration for running the complete InsightSwarm project using Docker Compose.

---

# Project Architecture

```text
Landing Page (Vite)       -> Port 3001
React Workspace (Vite)    -> Port 5173
FastAPI Backend           -> Port 8000
Streamlit Dashboard       -> Port 8501
```

---

# Services

The Docker Compose setup includes:

- Landing Page
- React Workspace
- FastAPI Backend
- Streamlit Dashboard

All services communicate over a shared Docker network.

---

# Prerequisites

Install:

- Docker Desktop
- Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

---

# Environment Variables

Create a `.env` file in the project root.

Required variables:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

# Docker Files

```text
devops/
├── docker-compose.yml
├── Dockerfile.python
├── Dockerfile.frontend
├── Dockerfile.landing
└── README_DEVOPS.md
```

### Shared Python Image

A single Python Docker image is shared between:

- FastAPI Backend
- Streamlit Dashboard

This avoids maintaining duplicate Dockerfiles and significantly reduces image size and build time.

---

# Persistent Volumes

Docker creates two shared volumes:

```text
logs
reports
```

These are mounted into both Backend and Streamlit containers.

Benefits:

- Shared application logs
- Shared generated PDF reports
- Streamlit always reads the latest backend logs
- Data persists across container restarts

---

# Running the Project

From the project root:

```bash
docker compose -f devops/docker-compose.yml up --build
```

This command will:

- Build required Docker images
- Create Docker network
- Create persistent volumes
- Start all services

---

# Subsequent Runs

```bash
docker compose -f devops/docker-compose.yml up
```

---

# Access the Application

### Landing Page

```
http://localhost:3001
```

### React Workspace

```
http://localhost:5173
```

### FastAPI Backend

```
http://localhost:8000
```

### Swagger Documentation

```
http://localhost:8000/docs
```

### Streamlit Dashboard

```
http://localhost:8501
```

---

# Stopping Containers

```bash
docker compose -f devops/docker-compose.yml down
```

---

# Rebuilding Images

```bash
docker compose -f devops/docker-compose.yml up --build
```

Force rebuild:

```bash
docker compose -f devops/docker-compose.yml build --no-cache
```

---

# Viewing Containers

```bash
docker ps
```

---

# Viewing Logs

All services:

```bash
docker compose -f devops/docker-compose.yml logs -f
```

Backend only:

```bash
docker compose -f devops/docker-compose.yml logs -f backend
```

Frontend:

```bash
docker compose -f devops/docker-compose.yml logs -f frontend
```

Landing:

```bash
docker compose -f devops/docker-compose.yml logs -f landing
```

Streamlit:

```bash
docker compose -f devops/docker-compose.yml logs -f streamlit
```

---

# Troubleshooting

## Port Already in Use

Stop the conflicting application or modify the port mapping in `docker-compose.yml`.

---

## Docker Desktop Not Running

Ensure Docker Desktop is running before executing Docker commands.

---

## Missing Environment Variables

Verify the root `.env` contains:

```env
GROQ_API_KEY
TAVILY_API_KEY
```

---

## Backend PDF Generation Issues

The shared Python image already includes the required Linux dependencies for WeasyPrint.

Rebuild if needed:

```bash
docker compose -f devops/docker-compose.yml build backend --no-cache
```

---

## Research History or Agent Tracker Not Updating

Both Backend and Streamlit share:

- logs volume
- reports volume

If changes are not reflected:

```bash
docker compose -f devops/docker-compose.yml down
docker compose -f devops/docker-compose.yml up --build
```

---

# Development Notes

- Backend uses FastAPI + Uvicorn
- React Workspace uses React + Vite
- Landing Page is an independent Vite application
- Streamlit runs independently on port 8501
- Backend and Streamlit share a common Python Docker image
- Docker Compose orchestrates all services through a shared Docker network
- Shared Docker volumes synchronize logs and generated reports
- Environment variables are loaded from the root `.env`
- Database initializes automatically during backend startup
- Service-to-service communication inside Docker uses Docker networking

---

# Verification Checklist

After starting containers:

- [ ] Landing Page loads
- [ ] React Workspace loads
- [ ] Backend responds
- [ ] Swagger UI works
- [ ] Streamlit Dashboard loads
- [ ] Research workflow completes
- [ ] PDF download works
- [ ] Research History loads correctly
- [ ] Agent Tracker updates in real time

---

# Team Usage

Clone repository

Create `.env`

Start Docker Desktop

Run:

```bash
docker compose -f devops/docker-compose.yml up --build
```

No manual installation of:

- Python
- Node.js
- npm packages
- pip packages
- Streamlit
- System libraries

is required.

Everything runs inside Docker containers.
>>>>>>> 2712553f1781ff4afb12f126aa849174ce06609c
