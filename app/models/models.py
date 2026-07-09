import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    topic = Column(String, nullable=False)
    instructions = Column(Text, nullable=True)
    depth = Column(String, default="standard") # e.g., standard, deep
    status = Column(String, default="pending") # pending, running, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    report = relationship("Report", back_populates="run", uselist=False)

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("research_runs.id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Store sections and citations as structured JSON for easy rendering later
    content_json = Column(JSON, nullable=False) 
    
    # Expiry tracking for cleanup (from your plan)
    expires_at = Column(DateTime, nullable=True)

    run = relationship("ResearchRun", back_populates="report")
    file = relationship("ReportFile", back_populates="report", uselist=False)

class ReportFile(Base):
    __tablename__ = "report_files"

    id = Column(String, primary_key=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    file_path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, default="application/pdf")

    report = relationship("Report", back_populates="file")