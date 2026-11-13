import asyncio
from app.database import Base, engine, SessionLocal
from app.services.discovery import run_discovery

async def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = await run_discovery(db)
        print(result)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())