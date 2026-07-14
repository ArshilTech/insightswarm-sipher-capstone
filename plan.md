# Plan: FastAPI + LangGraph Research Site With PDF Download

## Goal
Build a website where a user submits a research request, the system runs a multi-agent research workflow, and the final research content is rendered as a PDF that the user can download from the website.

## Section 1: Completed

- FastAPI application startup is wired in [app/main.py](app/main.py).
- Core database models exist for research runs, reports, and report files in [app/models/models.py](app/models/models.py).
- Request and response schemas exist in [app/models/schemas.py](app/models/schemas.py).
- The LangGraph workflow is implemented in [app/graphs/research_graph.py](app/graphs/research_graph.py) with intake, planning, research, synthesis, verification, and rendering nodes.
- Background research execution creates report records and updates run state in [app/api/routes.py](app/api/routes.py).
- Markdown-to-PDF generation is implemented in [app/services/pdf_service.py](app/services/pdf_service.py).
- Backend endpoints exist for starting research, checking status, fetching report metadata, and downloading the generated PDF in [app/api/routes.py](app/api/routes.py).

## Section 2: To Implement

- Build the website UI for submitting research requests, showing progress, and exposing the download link.
- Add stronger persistence and file lifecycle management, including cleanup for expired or abandoned reports.
- Expand the web research tooling and citation handling so the workflow can collect and normalize sources more reliably.
- Add automated tests for graph transitions, report generation, and download behavior.
- Add logging and observability for run progress, source usage, and PDF generation failures.
- Prepare deployment settings, production storage, and request hardening for release.

## Recommended Build Order

1. Finish the frontend submission and download flow.
2. Add persistence cleanup and expiry handling.
3. Strengthen the research and verification workflow.
4. Add tests and observability.
5. Prepare deployment and production storage.

## Output Behavior

- The user should receive a downloadable PDF after the research finishes.
- The website should provide a stable download link or button.
- The report should remain linked to the research run for later access if persistence is enabled.