# Plan: FastAPI + LangGraph Research Site With PDF Download

## Goal
Build a website where a user submits a research request, the system runs a multi-agent research workflow, and the final research content is rendered as a PDF that the user can download from the website.

## Step-by-Step Implementation

1. Define the user flow.
   - User enters a research topic or question in the website.
   - The backend creates a research job and starts the LangGraph workflow.
   - The workflow gathers sources, synthesizes findings, and produces a final report.
   - The final report is converted into a PDF.
   - The website shows a download link for the generated PDF.

2. Create the project structure.
   - Set up `FastAPI` for the backend API.
   - Set up `LangGraph` for multi-agent orchestration.
   - Add a frontend page for submitting research requests and downloading PDFs.
   - Add a storage layer for research runs, report metadata, and generated files.

3. Define the core data models.
   - Research request model: topic, instructions, desired depth, and output format.
   - Run model: id, status, timestamps, progress, and error fields.
   - Source model: title, url, snippet, and relevance score.
   - Report model: title, sections, citations, and summary text.
   - File model: PDF path, filename, MIME type, and download URL.

4. Build the LangGraph workflow.
   - Add a planner agent to break the topic into sub-questions.
   - Add parallel research agents to collect evidence from the web.
   - Add a synthesis agent to combine the findings into a structured report.
   - Add a verifier agent to check factual consistency and citation coverage.
   - Add a final formatting step to produce report content ready for PDF generation.

5. Implement web research tools.
   - Create search and fetch helpers for public web sources.
   - Normalize extracted content into a consistent source format.
   - Filter low-quality or duplicate sources.
   - Track citations so each important claim can point to evidence.

6. Generate the report content.
   - Convert the final research state into a structured report document.
   - Use sections like overview, findings, analysis, sources, and conclusion.
   - Include citations inline or in footnotes.
   - Store the rendered text separately from the PDF artifact for traceability.

7. Convert the report to PDF.
   - Use a PDF generation approach such as HTML-to-PDF or direct PDF rendering.
   - Apply a clear document template with title, section headers, page numbers, and branding.
   - Ensure the PDF is readable on desktop and mobile viewers.
   - Save the PDF to a file store or object storage.

8. Expose backend endpoints.
   - `POST /research` to start a new research job.
   - `GET /research/{id}` to check status and progress.
   - `GET /research/{id}/report` to fetch report metadata.
   - `GET /research/{id}/download` to return or redirect to the PDF file.

9. Build the website UI.
   - Create a form to submit research topics.
   - Show job progress while research is running.
   - Display the report summary when the job finishes.
   - Show a prominent PDF download button or link.
   - Provide error messaging if research or PDF generation fails.

10. Add persistence and file handling.
   - Store run state in a database.
   - Store generated PDF files in a durable location.
   - Keep report metadata so files can be re-downloaded later.
   - Add cleanup rules for expired or abandoned research jobs.

11. Add background execution.
   - Run the LangGraph workflow in the background for long research tasks.
   - Update run progress as each agent finishes.
   - Prevent the web request from timing out while the report is being generated.
   - Notify the frontend when the PDF is ready.

12. Add quality checks.
   - Test agent transitions in LangGraph.
   - Test that the verifier blocks unsupported claims.
   - Test PDF generation with a sample report.
   - Test the download endpoint returns the correct file.
   - Test the UI can display the final download link.

13. Add logging and observability.
   - Log each run id and workflow step.
   - Record source URLs used in the report.
   - Capture PDF generation errors separately from research errors.
   - Add tracing so failed runs can be debugged quickly.

14. Prepare for deployment.
   - Configure environment variables for API keys and storage.
   - Serve the backend behind a production ASGI server.
   - Store generated PDFs in a reliable cloud or server storage layer.
   - Add basic rate limiting and request validation.

## Recommended Build Order

1. Create the FastAPI project skeleton.
2. Implement the request and run models.
3. Build the LangGraph workflow.
4. Add web research tools.
5. Implement report synthesis.
6. Add PDF generation.
7. Expose API endpoints.
8. Build the download page in the website.
9. Add persistence and background jobs.
10. Add tests and observability.

## Implementation Checklist

### 1. Recommended Stack

- Backend: FastAPI.
- Orchestration: LangGraph.
- Schemas: Pydantic v2.
- Database: SQLite for runs, report metadata, and expiration tracking.
- Background jobs: FastAPI background tasks for the first prototype.
- Template rendering: Jinja2 for HTML report templates.
- PDF generation: HTML-to-PDF with WeasyPrint as the default choice.
- File storage: S3-compatible object storage or local disk for development.
- Download links: temporary signed URLs with expiry.

### 2. API Endpoints

- `POST /api/research`.
   - Accepts topic, user instructions, and optional depth.
   - Creates a run record and starts the workflow.
- `GET /api/research/{run_id}`.
   - Returns run status, progress, and error state.
- `GET /api/research/{run_id}/report`.
   - Returns report metadata, summary, and PDF availability.
- `POST /api/research/{run_id}/pdf-link`.
   - Generates a temporary signed download link.
- `GET /api/research/{run_id}/download`.
   - Redirects to the signed PDF URL or streams the file directly.

### 3. LangGraph Nodes

- `intake_node`.
   - Validates request data and initializes graph state.
- `plan_node`.
   - Breaks the topic into sub-questions and research tasks.
- `research_node_group`.
   - Runs parallel web research agents for each sub-question.
- `collect_node`.
   - Deduplicates sources and ranks evidence.
- `synthesize_node`.
   - Produces the final written report content.
- `verify_node`.
   - Checks claim coverage, source quality, and citation completeness.
- `render_html_node`.
   - Converts the report structure into HTML.
- `pdf_node`.
   - Converts HTML into a PDF file and stores it.
- `finalize_node`.
   - Writes status, file metadata, and expiry timestamps.

### 4. Suggested File Layout

- `app/main.py` for FastAPI app creation.
- `app/api/routes.py` for research endpoints.
- `app/graphs/research_graph.py` for LangGraph state and transitions.
- `app/agents/planner.py` for task decomposition.
- `app/agents/researcher.py` for web research.
- `app/agents/synthesizer.py` for report drafting.
- `app/agents/verifier.py` for claim checking.
- `app/services/pdf_service.py` for HTML-to-PDF conversion.
- `app/services/storage_service.py` for file upload and signed URLs.
- `app/services/report_service.py` for report assembly.
- `app/models/*.py` for request, run, source, and report schemas.
- `app/templates/report.html` for the PDF HTML template.
- `tests/` for workflow, API, and PDF generation tests.

### 5. PDF Generation Flow

1. Build a structured report object from the final graph state.
2. Render the report object into an HTML template.
3. Convert the HTML to a PDF using WeasyPrint.
4. Save the PDF to storage with a predictable path like `reports/{run_id}.pdf`.
5. Generate a temporary signed URL with a fixed expiry window.
6. Return the signed link to the frontend for download.

### 6. Expiration Strategy

- Store `expires_at` on each report record.
- Reject download requests after expiry.
- Run a scheduled cleanup job to delete expired PDF files and stale database rows.
- Keep the expiry window short enough to manage storage, but long enough for the user to download the file comfortably.

### 7. Frontend Behavior

- Show a submit form for the research topic.
- Poll run status or subscribe to updates until the report is ready.
- Display a download button once the PDF is available.
- Show the expiry time next to the download button.
- Disable or hide the link after expiration.

### 8. First Milestone

- Create the API contract and data models.
- Implement the LangGraph workflow without PDF generation first.
- Add HTML report rendering.
- Add PDF generation and signed link generation.
- Add the download endpoint and cleanup job.

### 9. Validation Checklist

- Confirm a run can be created and completed end-to-end.
- Confirm the verifier runs before PDF generation.
- Confirm the PDF opens correctly and contains the expected sections.
- Confirm signed links expire and are rejected after expiry.
- Confirm expired PDFs are removed by the cleanup job.

## Output Behavior

- The user should receive a downloadable PDF after the research finishes.
- The website should provide a stable download link or button.
- The report should remain linked to the research run for later access if persistence is enabled.

## Open Decisions

1. PDF generation should use HTML-to-PDF, because it is the simplest way to produce a polished report with reusable templates and predictable layout.
2. Downloads should use temporary signed links, so users can securely access the PDF without exposing the file store directly.
3. Completed reports should expire after a fixed time, so old artifacts are cleaned up automatically and storage stays manageable.