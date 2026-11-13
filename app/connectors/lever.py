from datetime import datetime
import httpx
from app.config import settings
from app.connectors.base import NormalizedJob

class LeverConnector:
    name = "lever"
    base_url = "https://api.lever.co/v0/postings/{site}?mode=json"

    async def fetch_jobs(self, site: str) -> list[NormalizedJob]:
        url = self.base_url.format(site=site)
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        jobs = []
        for item in payload[:settings.max_jobs_per_source]:
            categories = item.get("categories") or {}
            location = categories.get("location")
            workplace = (item.get("workplaceType") or "").lower()
            description = " ".join(filter(None, [
                item.get("descriptionPlain"),
                item.get("additionalPlain")
            ]))
            remote = workplace == "remote" or "remote" in (str(location) + " " + description[:3000]).lower()
            created = item.get("createdAt")
            try:
                posted_at = datetime.fromtimestamp(created / 1000).astimezone() if created else None
            except (ValueError, TypeError, OSError):
                posted_at = None

            jobs.append(NormalizedJob(
                source=self.name,
                source_job_id=str(item.get("id")),
                company=site,
                title=item.get("text") or "Untitled",
                location=location,
                remote=remote,
                employment_type=categories.get("commitment"),
                description=description,
                job_url=item.get("hostedUrl") or item.get("applyUrl") or "",
                posted_at=posted_at
            ))
        return jobs
