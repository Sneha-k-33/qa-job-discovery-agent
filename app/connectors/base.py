from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass
class NormalizedJob:
    source: str
    source_job_id: str
    company: str
    title: str
    location: str | None
    remote: bool
    employment_type: str | None
    description: str | None
    job_url: str
    posted_at: datetime | None = None

class JobSource(Protocol):
    name: str
    async def fetch_jobs(self, company_key: str) -> list[NormalizedJob]: ...
