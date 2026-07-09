from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_async_session

from app.models.schemas import ResearchRequest, ResearchRunResponse
from app.models.models import ResearchRun

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
    
    # 3. Return the SQLAlchemy object; FastAPI will automatically serialize 
    # it into the ResearchRunResponse Pydantic model
    return new_run