import uuid
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    depth: Mapped[str] = mapped_column(String, default="standard") # e.g., standard, deep
    status: Mapped[str] = mapped_column(String, default="pending") # pending, running, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    report: Mapped["Report | None"] = relationship("Report", back_populates="run", uselist=False)

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("research_runs.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Store sections and citations as structured JSON for easy rendering later
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False) 
    
    # Expiry tracking for cleanup (from your plan)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    run: Mapped[ResearchRun] = relationship("ResearchRun", back_populates="report")
    file: Mapped["ReportFile | None"] = relationship("ReportFile", back_populates="report", uselist=False)

class ReportFile(Base):
    __tablename__ = "report_files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    report_id: Mapped[str] = mapped_column(String, ForeignKey("reports.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, default="application/pdf")

    report: Mapped[Report] = relationship("Report", back_populates="file")