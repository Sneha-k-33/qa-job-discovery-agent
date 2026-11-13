import json
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models import JobListing, DiscoveryRun

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        httpx.post(url, json=payload, timeout=10.0)
    except Exception as e:
        print(f"Telegram alert error: {e}")

def load_boards():
    path = ROOT_DIR / "config" / "boards.json"
    if not path.exists():
        return {"free_boards": []}
    return json.loads(path.read_text(encoding="utf-8"))

async def run_discovery(db: Session) -> dict:
    run = DiscoveryRun(status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    config = load_boards()
    seen = added = checked = 0
    errors = []

    free_boards = config.get("free_boards", [])

    async with httpx.AsyncClient() as client:
        for board in free_boards:
            checked += 1
            board_name = board.get("name", "Unknown Board")
            url = board.get("url")
            provider = board.get("provider")

            if not url:
                continue

            try:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15.0)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                fetched_items = []

                if provider == "himalayas":
                    fetched_items = data.get("jobs", [])
                elif provider == "remoteok":
                    items = data[1:] if isinstance(data, list) and len(data) > 1 else data
                    fetched_items = [
                        item for item in items 
                        if any(kw in (item.get("position", "") or "").lower() for kw in ["qa", "quality assurance", "test", "sdet"])
                    ]
                elif isinstance(data, list):
                    fetched_items = data
                elif isinstance(data, dict):
                    fetched_items = data.get("jobs", data.get("data", []))

                for item in fetched_items[:15]:
                    if provider == "himalayas":
                        title = item.get("title")
                        company = item.get("companyName")
                        job_url = item.get("applicationLink") or item.get("guid")
                        source_id = str(item.get("guid") or job_url)
                        pub_timestamp = item.get("pubDate")
                        posted_at = datetime.fromtimestamp(pub_timestamp, tz=timezone.utc) if pub_timestamp else None
                        desc = item.get("description")
                    else:
                        title = item.get("position") or item.get("title")
                        company = item.get("company")
                        job_url = item.get("url") or item.get("apply_url")
                        source_id = str(item.get("id") or job_url)
                        posted_at = datetime.now(timezone.utc)
                        desc = item.get("description")

                    if not title or not job_url:
                        continue

                    seen += 1

                    exists = db.scalar(select(JobListing).where(
                        JobListing.source == provider,
                        JobListing.source_job_id == source_id
                    ))

                    if exists:
                        exists.active = True
                        exists.title = title
                        exists.job_url = job_url
                        db.commit()
                        continue

                    new_job = JobListing(
                        source=provider or "free_board",
                        source_job_id=source_id,
                        company=company or "Unknown",
                        title=title,
                        job_url=job_url,
                        remote=True,
                        description=desc,
                        posted_at=posted_at,
                        active=True
                    )
                    db.add(new_job)
                    db.commit()
                    added += 1

                    alert_text = f"✨ *New QA Job Discovered!*\n\n*Title:* {title}\n*Company:* {company}\n[Apply Here]({job_url})"
                    send_telegram_alert(alert_text)

            except Exception as e:
                errors.append(f"{board_name}: {str(e)}")

    # These lines correctly belong at the end of run_discovery()
    run.completed_at = datetime.now(timezone.utc)
    run.sources_checked = checked
    run.jobs_seen = seen
    run.jobs_added = added
    run.errors = "; ".join(errors) if errors else None
    run.status = "completed"
    db.commit()

    return {
        "run_id": run.id,
        "status": run.status,
        "sources_checked": checked,
        "matching_jobs_seen": seen,
        "new_jobs_added": added,
        "errors": errors
    }

def load_boards():
    # Use Path("config/boards.json") directly so it matches your current directory
    path = Path("config/boards.json")
    if not path.exists():
        # Fallback to parent if run from inside an app/ subdirectory
        path = ROOT_DIR / "config" / "boards.json"
    if not path.exists():
        return {"free_boards": []}
    return json.loads(path.read_text(encoding="utf-8"))