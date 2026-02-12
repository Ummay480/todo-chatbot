from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from typing import Generator
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/petrol_pump_ledger")

# Create a Base class for declarative models
Base = declarative_base()

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain in the pool
    max_overflow=20,  # Number of connections beyond pool_size that can be opened
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL query logging
)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db_session() -> Generator:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias for FastAPI dependency injection
get_db = get_db_session


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database
    """
    # Import models here to avoid circular imports
    from ..models.User import User
    from ..models.Task import Task
    from ..models.Conversation import Conversation
    from ..models.Message import Message

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def test_database_connection():
    """
    Test the database connection
    """
    try:
        with get_db_connection() as db:
            # Execute a simple query to test the connection
            result = db.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_pool_stats():
    """
    Get connection pool statistics
    """
    pool = engine.pool
    stats = {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "recycled": getattr(pool, '_recycle_pool', []) if hasattr(pool, '_recycle_pool') else []
    }
    return stats


def init_database():
    """
    Initialize the database connection and create tables
    """
    try:
        # Test the connection first
        if test_database_connection():
            logger.info("Database connection established successfully")

            # Create tables
            create_tables()
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Failed to establish database connection")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False