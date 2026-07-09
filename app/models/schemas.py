from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Requests ---

class ResearchRequest(BaseModel):
    topic: str = Field(..., description="The main research topic or question")
    instructions: Optional[str] = Field(None, description="Custom instructions for the agents")
    depth: str = Field("standard", description="Desired depth: 'standard' or 'deep'")
    output_format: str = Field("pdf", description="Requested output format")

# --- Responses ---

class ResearchRunResponse(BaseModel):
    id: str
    topic: str
    status: str
    progress: int
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReportFileResponse(BaseModel):
    filename: str
    mime_type: str
    download_url: str # We will generate this dynamically later

    class Config:
        from_attributes = True