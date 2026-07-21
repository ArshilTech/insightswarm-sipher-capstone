Slide 1 — Opening / Self-introduction

- Time: 45s
- Speaker: Arshil Masood (opening)
- Script:
  Good [morning/afternoon], everyone — I'm Arshil Masood, frontend developer and presenter for team "404 Competition not found." Today we'll walk you through InsightSwarm: a multi-agent research assistant that turns complex questions into structured research reports and a reproducible research history.
  Hook line: "We don't just search the web — we orchestrate teams of AI agents to turn noise into insight."

Slide 2 — Project Title & Elevator Pitch

- Time: 45s
- Speaker: Arshil Masood
- Script:
  Project: InsightSwarm — Intelligent multi-agent research platform.
  Quick idea: Users submit research topics via a lightweight landing page; a backend coordinates multiple AI agents that gather, reason over, and synthesize findings; outputs are a downloadable PDF report, a React report viewer, and a Streamlit dashboard to trace agent activity and history.
  Why it matters: It accelerates evidence gathering, enforces structure, and makes research auditable.

Slide 3 — System Level Architecture (visual)

- Time: 60s
- Speaker: Arshil Masood (overview)
- Visual: Use the attached system-level architecture screenshot.
- Script:
  Walkthrough: The user enters on the landing page, then can access the research app or the dashboard. The backend server coordinates requests and sends them to the research engine where AI agents retrieve web data, reason, and write outputs. Results are stored in the database and exported as PDF reports.
  Repo pointers: backend entry is `app/main.py`, API routes live in `app/api/routes.py`, DB helpers in `db/database.py`, and PDF logic in `services/pdf_service.py`.

Slide 4 — Frontend: Landing page, Research page, Streamlit dashboard

- Time: 90s total (30s per sub-section)
- Speakers: Arshil Masood (landing + handoff), Two members for research page and dashboard (split)
- Script — Landing page (30s):
  The landing page is a static HTML/CSS entry (see `frontend/landing/index.html` and `frontend/landing/css/styles.css`). It introduces InsightSwarm, gives a short demo path, and links to the research app.

- Script — Research page (30s, Presenter A & B):
  The research app is a React + Tailwind SPA in `frontend/React+Tailwind/src`. Users submit topics, view active jobs, and open generated reports in-app. It talks to the FastAPI backend (`app/main.py`) to create jobs and poll status.
  Presenter A: Explain UI flow — topic form, status list, opening a report.
  Presenter B: Explain how the front-end displays structured results and interacts with the backend APIs.

- Script — Streamlit Dashboard (30s, Presenter C & D):
  The Streamlit app (`streamlit/streamlit-app.py`) is a lightweight agent tracker and research history viewer. It connects to the same SQLite metadata DB and visualizes agent progress, job logs, and allows quick re-run of a job for debugging.
  Presenter C: Show the agent tracker and history view.
  Presenter D: Summarize how Streamlit helps with transparency and debugging.

Slide 5 — Backend Architecture (visual)

- Time: 60s
- Speakers: Two backend members (split)
- Visual: Use the attached backend architecture image.
- Script:
  Explain FastAPI backend responsibilities: accept job requests, persist metadata to SQLite (`db/database.py`), enqueue or trigger the LangGraph-based research workflow, and expose endpoints for status and results.
  Member 1: Walk backend request lifecycle and DB usage.
  Member 2: Explain integrations — model inference, web retrieval (search API), and the agents orchestration components.

Slide 6 — AI Research Pipeline

- Time: 70s
- Speaker: Backend/AI member
- Script:
  Steps: 1) Intake: receive topic + constraints. 2) Planning: agent roles are defined (retriever, extractor, reasoner, summarizer). 3) Retrieval: web APIs and cached sources pulled. 4) Reasoning: agents synthesize structured facts and citations. 5) Report assembly: `services/pdf_service.py` composes the final PDF and metadata.
  Emphasize multi-agent collaboration and how each agent focuses on a subtask for robustness and traceability.

Slide 7 — Validation Layer

- Time: 50s
- Speaker: Backend/QA member
- Script:
  Purpose: prevent unauthorized or unsafe research, ensure outputs meet format and citation rules, and validate findings against simple heuristics.
  Implementation notes: validation checks occur in the backend workflow before finalizing results — filters for blacklisted topics, citation count minimums, and basic factuality checks (e.g., cross-source agreement). Metadata is persisted so manual review is possible via the Streamlit dashboard.

Slide 8 — DevOps & Deployment

- Time: 50s
- Speaker: DevOps member
- Script:
  Repos include `devops/Dockerfile.python`, `devops/docker-compose.yml`, and other Dockerfiles for frontend and landing. The system is containerized: the FastAPI backend, React frontend, and Streamlit dashboard run as separate services.
  CI/CD notes: we containerize and orchestrate locally with Docker Compose, and we recommend a Kubernetes deployment for horizontal scaling of agents and model inference services.

Slide 9 — Advantages / Differentiators

- Time: 55s
- Speaker: Arshil Masood
- Visual: Use the attached "Advantages" slide image
- Script:
  Highlight bullets: Multi-agent collaboration, live web intelligence, structured reasoning, research-ready PDFs, transparent execution (agent tracker), and safeguards preventing restricted queries.
  Tie each advantage to a concrete repo artifact (example: agent tracker → `streamlit/streamlit-app.py`; PDF reports → `services/pdf_service.py`).

Slide 10 — Team

- Time: 35s
- Speaker: Arshil Masood
- Visual: Use attached team slide
- Script:
  Quick roll call: Team Lead — Kamran Rizvi. Frontend: Arshil Masood, Mohammad Faraz, Abdullah Ansari, Affan Ansari, Ayushmaan Vaibhav. Backend + DevOps: Syed Abad Mustafa, Ghazi Haider, Anubhav Bharadwaj, Sayed Mohd Zaid.
  Invite backend and frontend members to stand by for a short Q&A.

Slide 11 — End & Thank You

- Time: 40s
- Speaker: Arshil Masood (closing)
- Script:
  Closing: "Thank you for your time — InsightSwarm makes structured, auditable research fast and repeatable. We're happy to answer questions or give a live demo now." Provide contact/next steps.

Appendix: Quick repo map (for Q&A)

- `app/main.py` — FastAPI server entry
- `app/api/routes.py` — API endpoints
- `db/database.py` — SQLite helpers
- `services/pdf_service.py` — PDF generation pipeline
- `frontend/React+Tailwind/src` — React research app
- `frontend/landing` — static landing page
- `streamlit/streamlit-app.py` — agent tracker + history UI

Timing summary: total ≈ 10 minutes. Slide timings are adjustable in small increments.
