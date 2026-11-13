from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings, ROOT_DIR

class Base(DeclarativeBase):
    pass

if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url.replace("sqlite:///", "", 1)
    resolved = (ROOT_DIR / db_path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    engine_url = f"sqlite:///{resolved.as_posix()}"
    engine = create_engine(engine_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
