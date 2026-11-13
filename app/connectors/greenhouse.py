from datetime import datetime, timezone
import httpx
from app.config import settings
from app.connectors.base import NormalizedJob

class GreenhouseConnector:
    name = "greenhouse"
    base_url = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

    async def fetch_jobs(self, board: str) -> list[NormalizedJob]:
        url = self.base_url.format(board=board)
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        jobs = []
        for item in payload.get("jobs", [])[:settings.max_jobs_per_source]:
            location = (item.get("location") or {}).get("name")
            content = item.get("content") or ""
            offices = item.get("offices") or []
            remote_text = " ".join([str(location or ""), content[:4000]]).lower()
            remote = any(word in remote_text for word in ("remote", "work from home", "distributed"))
            posted = item.get("updated_at")
            try:
                posted_at = datetime.fromisoformat(posted.replace("Z", "+00:00")) if posted else None
            except (ValueError, AttributeError):
                posted_at = None

            jobs.append(NormalizedJob(
                source=self.name,
                source_job_id=str(item.get("id")),
                company=board,
                title=item.get("title") or "Untitled",
                location=location,
                remote=remote,
                employment_type=None,
                description=content,
                job_url=item.get("absolute_url") or "",
                posted_at=posted_at
            ))
        return jobs
