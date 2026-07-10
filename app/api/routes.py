from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_async_session
from typing import Any

from app.models.schemas import ResearchRequest, ResearchRunResponse
from app.models.models import ResearchRun

from app.graphs.research_graph import research_graph, ResearchState

router = APIRouter()

@router.post("/research", response_model=ResearchRunResponse, status_code=201)
async def start_research(
    request: ResearchRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Map the incoming Pydantic request to our SQLAlchemy model
    new_run = ResearchRun(
        topic=request.topic,
        instructions=request.instructions,
        depth=request.depth
        # status and progress will default to "pending" and 0 automatically
    )
    
    # 2. Add to session and commit to the database asynchronously
    session.add(new_run)
    try:
        await session.commit()
        await session.refresh(new_run) # Refresh to get the generated ID and timestamps
    except Exception as e:
        await session.rollback()
        print(f"Database error: {e}") # For local debugging
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
        "error": ""
    }

    # 4. Execute the research graph asynchronously
    try:
        print(f"Starting graph execution for run: {new_run.id}")
        # Using ainvoke for asynchronous execution
        final_state: dict[str, Any] = await research_graph.ainvoke(initial_state)
        print(f"Graph execution completed. Final state report length: {len(final_state['final_report'])}")
        
        # Update success status here as well
        new_run.status = "completed"
        new_run.progress = 100
        await session.commit()
        
    except Exception as e:
        print(f"Graph execution error: {e}")
        
        new_run.status = "failed"
        new_run.progress = 0
        new_run.error_message = str(e)
        
        session.add(new_run)  # Ensure the session tracks the updated object
        await session.commit()
        
        raise HTTPException(status_code=500, detail="Research graph execution failed.")
    
    # 5. Return the new research run details to the client
    return new_run