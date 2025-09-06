from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with error handling
try:
    logger.info(f"Attempting to connect to database: {settings.database_url}")
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Database engine created successfully")
except ImportError as e:
    logger.error(f"⚠️  Database driver not available: {e}")
    logger.error("Install with: pip install psycopg2-binary")
    engine = None
    SessionLocal = None
except Exception as e:
    logger.error(f"⚠️  Database connection failed: {e}")
    logger.error("Make sure PostgreSQL is running on localhost:5433")
    engine = None
    SessionLocal = None

Base = declarative_base()
