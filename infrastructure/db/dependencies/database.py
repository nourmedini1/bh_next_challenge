from typing import Generator
from sqlalchemy.orm import Session
from db.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    if SessionLocal is None:
        raise Exception("Database not initialized. Please install psycopg2-binary and ensure PostgreSQL is running.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
