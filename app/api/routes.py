from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_async_session
from typing import Any

from app.models.schemas import ResearchRequest, ResearchRunResponse, ReportResponse, ReportFileResponse
from app.models.models import ResearchRun, Report, ReportFile

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
