from datetime import datetime
from pydantic import BaseModel, ConfigDict

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source: str
    company: str
    title: str
    location: str | None
    remote: bool
    employment_type: str | None
    job_url: str
    posted_at: datetime | None
    discovered_at: datetime
    active: bool
