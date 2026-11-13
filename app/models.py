from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class JobListing(Base):
    __tablename__ = "job_listings"
    __table_args__ = (UniqueConstraint("source", "source_job_id", name="uq_source_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    source_job_id: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_url: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    keywords: Mapped[str | None] = mapped_column(String(1000), nullable=True)

class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sources_checked: Mapped[int] = mapped_column(Integer, default=0)
    jobs_seen: Mapped[int] = mapped_column(Integer, default=0)
    jobs_added: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="running")
