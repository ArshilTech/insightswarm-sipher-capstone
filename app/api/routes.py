from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_async_session
from typing import Any

from app.models.schemas import ResearchRequest, ResearchRunResponse, ReportResponse, ReportFileResponse
from app.models.models import ResearchRun, Report, ReportFile

from app.models.models import ExecutiveSummary
from app.models.schemas import ExecutiveSummaryResponse
from app.services.summary_service import generate_executive_summary_text, generate_executive_summary_pdf

from app.graphs.research_graph import research_graph, ResearchState

from app.db.database import async_session_maker

from app.services.pdf_service import generate_pdf_report

from fastapi.responses import FileResponse
from sqlalchemy.orm import selectinload
from sqlalchemy import select
import os
import re
from app.core import get_logger, get_run_logger

router = APIRouter()
logger = get_logger(__name__)

# --- Background Task Function ---
# We use a separate database session maker here because the request-scoped 
# session closes before the background task finishes.

async def run_research_background(initial_state: ResearchState):
    run_logger = get_run_logger(__name__, initial_state['run_id'])
    async with async_session_maker() as session:
        try:
            run_logger.info("Background task: Starting graph execution")
            final_state: dict[str, Any] = await research_graph.ainvoke(initial_state)
            
            final_markdown = final_state.get("final_report", "")

            # Remove the think block and all its contents
            final_markdown = re.sub(r"<think>.*?</think>", "", final_markdown, flags=re.DOTALL).strip()
            final_markdown = clean_latex(final_markdown)
            sources_list = final_state.get("sources", [])
            final_markdown = format_references_in_markdown(final_markdown, sources=sources_list)

            topic = final_state.get("topic", "research_report")
            pdf_path = None
            
            # Create the Report record in the database
            summary_text = ""
            if final_markdown:
                summary_text = final_markdown[:500] + ("..." if len(final_markdown) > 500 else "")

            new_report = Report(
                run_id=initial_state['run_id'],
                title=f"Research Report on {topic}",
                summary=summary_text,
                content_json={"raw_markdown": final_markdown}
            )

            session.add(new_report)
            await session.flush() # Flush to get the new report ID before committing
            
            # Generate PDF report on disk AFTER report is in the database
            pages_count = 1
            if final_markdown:
                try:
                    pdf_path, pages_count = generate_pdf_report(final_markdown, initial_state['run_id'])
                    run_logger.info(f"Background task: PDF report generated at {pdf_path} with {pages_count} pages.")
                    
                    # Create the ReportFile record to link the PDF to the report
                    report_file = ReportFile(
                        report_id=new_report.id,
                        file_path=pdf_path,
                        filename=f"{initial_state['run_id']}.pdf",
                        mime_type="application/pdf"
                    )
                    session.add(report_file)
                except Exception as pdf_error:
                    run_logger.error(f"Background task: PDF generation failed: {pdf_error}", exc_info=True)
                    # Continue without PDF, report still has markdown content
            
            # Calculate sources count
            citations = re.findall(r'\[\d+\]', final_markdown)
            sources_count = len(set(citations)) if citations else 0
            if sources_count == 0:
                links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', final_markdown)
                sources_count = len(set(links)) if links else 4

            new_report.content_json = {
                "raw_markdown": final_markdown,
                "pages": pages_count,
                "sources": sources_count
            }
            
            # Update the database with the final state
            run = await session.get(ResearchRun, initial_state['run_id'])
            if run:
                run.status = "completed"
                run.progress = 100
                await session.commit()
                run_logger.info("Background task: Run completely finalized with PDF.")

        except Exception as e:
            run_logger.error(f"Background task: Graph execution error: {e}", exc_info=True)
            run = await session.get(ResearchRun, initial_state['run_id'])
            if run:
                run.status = "failed"
                run.progress = 0
                run.error_message = str(e)
                await session.commit()

def clean_latex(text: str) -> str:
    # 1. Remove display math delimiters ($$) and inline math delimiters ($)
    text = text.replace("$$", "").replace("$", "")
    
    # 2. Clean up Dirac bra-ket notation (e.g., |\psi\rangle -> |psi>)
    text = re.sub(r'\\rangle', '>', text)
    text = re.sub(r'\\langle', '<', text)
    
    # 3. Strip the leading backslash from LaTeX words (e.g., \alpha -> alpha)
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    return text.strip()

def format_references_in_markdown(markdown_content: str, sources: list = None) -> str:
    """
    Finds or appends the References section in Markdown, strips links to make entries unclickable,
    and limits the section to top 5 reference entries.
    """
    # CRITICAL: Must use ^ at line start with MULTILINE to avoid matching anchor links like [References](#references) in TOC
    pattern = r'(^\s*#+\s*(?:\d+[\.\)]\s*)?References\s*:?\s*\n?)(.*)'
    match = re.search(pattern, markdown_content, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    if not match:
        if sources:
            top_sources = sources[:5]
            ref_entries = [f"{idx}. {src.get('title', 'Reference ' + str(idx))}" for idx, src in enumerate(top_sources, 1) if src.get('title')]
            if ref_entries:
                return markdown_content.strip() + "\n\n# References\n\n" + "\n".join(ref_entries) + "\n"
        return markdown_content

    header = match.group(1)
    refs_body = match.group(2)

    # Check if another header follows References
    next_header_match = re.search(r'\n(#+\s+.*)', refs_body)
    if next_header_match:
        following_content = refs_body[next_header_match.start():]
        refs_body = refs_body[:next_header_match.start()]
    else:
        following_content = ""

    lines = [line.strip() for line in refs_body.strip().split('\n') if line.strip()]
    cleaned_entries = []

    for line in lines:
        # Ignore HTML tags, KPI cards, or non-reference text
        if line.startswith("<") or line.startswith("{") or line.startswith("|"):
            continue
        line_clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        line_clean = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', line_clean, flags=re.IGNORECASE)
        line_clean = re.sub(r'\s*\(https?://[^\)]+\)', '', line_clean)
        line_clean = re.sub(r'\s*-\s*https?://\S+', '', line_clean)
        entry_text = re.sub(r'^(\d+[\.\)]\s*|-\s*|\*\s*)', '', line_clean).strip()
        if entry_text:
            cleaned_entries.append(entry_text)
        if len(cleaned_entries) == 5:
            break

    if not cleaned_entries and sources:
        top_sources = sources[:5]
        cleaned_entries = [src.get('title', f"Reference {idx}") for idx, src in enumerate(top_sources, 1) if src.get('title')]

    final_refs = [f"{idx}. {entry}" for idx, entry in enumerate(cleaned_entries, 1)]
    new_refs_section = "\n\n# References\n\n" + "\n".join(final_refs) + "\n\n" + following_content
    return markdown_content[:match.start()].strip() + new_refs_section

# --- API Endpoint to Start Research ---

@router.post("/research", response_model=ResearchRunResponse, status_code=201)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks, # Allows us to run the research graph in the background
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Map the incoming Pydantic request to our SQLAlchemy model
    new_run = ResearchRun(
        topic=request.topic,
        instructions=request.instructions,
        depth=request.depth,
        status = "running"
    )
    
    # 2. Add to session and commit to the database asynchronously
    session.add(new_run)
    try:
        await session.commit()
        await session.refresh(new_run) # Refresh to get the generated ID and timestamps
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}", exc_info=True) # For local debugging
        raise HTTPException(status_code=500, detail="Failed to save research run.")
    
    # 3. Prepare the initial state for LangGraph
    initial_state: ResearchState = {
        "run_id": str(new_run.id),
        "topic": new_run.topic,
        "instructions": new_run.instructions or "",
        "depth": new_run.depth,
        "sub_questions": [],
        "sources": [],
        "draft": "",
        "is_verified": False,
        "final_report": "",
        "error": "",
        "retry_count": 0
    }

    # 4. Schedule the background task to run the research graph
    background_tasks.add_task(run_research_background, initial_state)
    
    # 5. Return the new research run details to the client
    return new_run

# --- API Endpoint to List All Research Runs ---

@router.get("/research")
async def list_research_runs(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(ResearchRun).options(selectinload(ResearchRun.report)).order_by(ResearchRun.created_at.desc())
    result = await session.execute(stmt)
    runs = result.scalars().all()
    
    data = []
    for run in runs:
        agents_count = 5
        data.append({
            "id": run.id,
            "title": run.report.title if run.report else f"Research on {run.topic}",
            "status": run.status.capitalize(),
            "date": run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else "",
            "agents_used": agents_count
        })
    return {"data": data}

# --- API Endpoint to Check Research Status ---

@router.get("/research/{run_id}", response_model=ResearchRunResponse)
async def get_research_status(
    run_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    run = await session.get(ResearchRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found.")
    return run

# --- Report retrieval endpoint ---
@router.get("/research/{run_id}/report", response_model=ReportResponse)
async def get_report_metadata(
    run_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    # Fetch the report and eagerly load the associated file relationship
    stmt = select(Report).where(Report.run_id == run_id).options(selectinload(Report.file))
    result = await session.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this run.")
    
    # Create the response dictionary manually to inject the dynamic download URL
    response_data = {
        "id": report.id,
        "run_id": report.run_id,
        "title": report.title,
        "summary": report.summary,
        "file": report.file,
        "download_url": f"/api/research/{run_id}/download" if report.file else None,
        "content_json": report.content_json
    }

    return response_data

# --- Report file download endpoint ---
@router.get("/research/{run_id}/download")
async def download_report_pdf(
    run_id: str,
    inline: bool = False,
    session: AsyncSession = Depends(get_async_session)
):
    # Fetch the report and its associated file
    stmt = select(ReportFile).join(Report).where(Report.run_id == run_id)
    result = await session.execute(stmt)
    report_file = result.scalars().first()

    if not report_file:
        raise HTTPException(status_code=404, detail="PDF not generated yet or not found.")
    
    # Verify the file actually exists on the disk
    if not os.path.exists(report_file.file_path):
        raise HTTPException(status_code=500, detail="PDF record exists, but file is missing from disk.")
    
    # Serve the file for download or inline preview
    return FileResponse(
        path=report_file.file_path,
        filename=report_file.filename,
        media_type=report_file.mime_type,
        content_disposition_type="inline" if inline else "attachment"
    )

# --- Executive Summary generation endpoint ---
# Uses only the already-generated report's markdown — never re-invokes the research graph.
@router.post("/research/{run_id}/executive-summary", response_model=ExecutiveSummaryResponse)
async def create_executive_summary(
    run_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Report).where(Report.run_id == run_id).options(selectinload(Report.executive_summary))
    result = await session.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this run.")

    # Avoid a redundant LLM call if a summary was already generated for this report
    if report.executive_summary:
        existing = report.executive_summary
        return {
            "id": existing.id,
            "run_id": run_id,
            "content_markdown": existing.content_markdown,
            "download_url": f"/api/research/{run_id}/executive-summary/download" if existing.pdf_file_path else None
        }

    raw_markdown = (report.content_json or {}).get("raw_markdown", "")
    if not raw_markdown:
        raise HTTPException(status_code=400, detail="Report has no content to summarize.")

    summary_logger = get_run_logger(__name__, run_id)
    try:
        summary_markdown = generate_executive_summary_text(raw_markdown)
    except Exception as e:
        summary_logger.error(f"Executive summary generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate executive summary.")

    pdf_path = None
    try:
        pdf_path = generate_executive_summary_pdf(summary_markdown, run_id)
    except Exception as e:
        summary_logger.error(f"Executive summary PDF generation failed: {e}", exc_info=True)
        # Continue without a PDF — the markdown summary is still usable in the UI

    new_summary = ExecutiveSummary(
        report_id=report.id,
        content_markdown=summary_markdown,
        pdf_file_path=pdf_path
    )
    session.add(new_summary)
    await session.commit()
    await session.refresh(new_summary)

    return {
        "id": new_summary.id,
        "run_id": run_id,
        "content_markdown": new_summary.content_markdown,
        "download_url": f"/api/research/{run_id}/executive-summary/download" if pdf_path else None
    }

# --- Executive Summary file download endpoint ---
@router.get("/research/{run_id}/executive-summary/download")
async def download_executive_summary_pdf(
    run_id: str,
    inline: bool = False,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(ExecutiveSummary).join(Report).where(Report.run_id == run_id)
    result = await session.execute(stmt)
    summary = result.scalars().first()

    if not summary or not summary.pdf_file_path:
        raise HTTPException(status_code=404, detail="Executive summary PDF not found.")

    if not os.path.exists(summary.pdf_file_path):
        raise HTTPException(status_code=500, detail="Executive summary PDF record exists, but file is missing from disk.")

    return FileResponse(
        path=summary.pdf_file_path,
        filename=f"{run_id}_executive_summary.pdf",
        media_type="application/pdf",
        content_disposition_type="inline" if inline else "attachment"
    )

# --- Report file delete endpoint ---
@router.delete("/research/{run_id}/delete")
async def delete_report(
    run_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    # Fetch the research run, report, associated file, and executive summary so the entire item can be removed.
    stmt = select(ResearchRun).where(ResearchRun.id == run_id).options(
        selectinload(ResearchRun.report).selectinload(Report.file),
        selectinload(ResearchRun.report).selectinload(Report.executive_summary)
    )
    result = await session.execute(stmt)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Research run not found.")

    report = run.report

    if report:
        # Delete associated PDF file from disk if it exists
        if report.file and report.file.file_path and os.path.exists(report.file.file_path):
            try:
                os.remove(report.file.file_path)
                logger.info(f"Deleted PDF file at {report.file.file_path}")
            except Exception as e:
                logger.warning(f"Could not delete PDF file from disk ({report.file.file_path}): {e}")

        # Delete associated Executive Summary PDF file from disk if it exists
        if report.executive_summary and report.executive_summary.pdf_file_path and os.path.exists(report.executive_summary.pdf_file_path):
            try:
                os.remove(report.executive_summary.pdf_file_path)
                logger.info(f"Deleted Executive Summary PDF file at {report.executive_summary.pdf_file_path}")
            except Exception as e:
                logger.warning(f"Could not delete Executive Summary PDF file from disk ({report.executive_summary.pdf_file_path}): {e}")

        # Delete child rows first so report delete does not hit a Foreign Key constraint
        if report.file:
            await session.delete(report.file)
        if report.executive_summary:
            await session.delete(report.executive_summary)

        # Delete the report row
        await session.delete(report)

    # Delete the parent research run
    await session.delete(run)
    await session.commit()

    return {"detail": "Report and associated assets deleted successfully."}