"""Configuration for database connection and management."""

from os import getenv

from sqlmodel import create_engine, Session, select
from sqlalchemy.engine import make_url
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = getenv("DATABASE_URL")
UUID_SERVER_DEFAULT = func.gen_random_uuid()

# ### SQL MODEL ENGINE: ###
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

Base = declarative_base()


def _database_target() -> str:
    """Return a safe, human-readable DB target for logging."""
    try:
        db_url = DATABASE_URL or ""
        url = make_url(db_url)
        host = url.host or "unknown-host"
        port = url.port or "default"
        db_name = url.database or "unknown-db"
        return f"{host}:{port}/{db_name}"
    except Exception:
        return "unknown-target"


def validate_database_connection() -> bool:
    """Perform a lightweight startup DB connectivity check and log the outcome."""
    try:
        with Session(engine) as session:
            session.exec(select(1)).first()
        return True
    except Exception as exc:
        return False


def request_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
