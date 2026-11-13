from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from app.database import SessionLocal, engine, Base
from app.services.discovery import run_discovery

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

def scheduled_job_wrapper():
    db = SessionLocal()
    try:
        asyncio.run(run_discovery(db))
    except Exception as e:
        print(f"Scheduled discovery error: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background schedule (e.g., runs every 3 hours)
    scheduler.add_job(scheduled_job_wrapper, "interval", hours=3)
    scheduler.start()
    print("🤖 QA Job Discovery Scheduler started successfully!")
    yield
    scheduler.shutdown()

app = FastAPI(title="QA Job Agent", lifespan=lifespan)

# Dependency to get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "QA Job Agent is running with automated background discovery!"}

@app.post("/api/discover", summary="Trigger manual job discovery")
async def trigger_discovery(db: Session = Depends(get_db)):
    """
    Manually triggers the job discovery pipeline on demand.
    Fetches live listings from free sources and pushes Telegram notifications.
    """
    try:
        result = await run_discovery(db)
        return {
            "message": "Manual discovery run completed successfully!",
            "details": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

    from app.models import JobListing
from sqlalchemy import select

@app.get("/api/jobs", summary="View all discovered QA jobs")
def get_discovered_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    jobs = db.scalars(select(JobListing).order_by(JobListing.discovered_at.desc()).offset(skip).limit(limit)).all()
    return {
        "count": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "remote": j.remote,
                "url": j.job_url,
                "discovered_at": j.discovered_at
            } for j in jobs
        ]
    }