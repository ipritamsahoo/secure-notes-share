import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Configuration ---
class Settings:
    PROJECT_NAME: str = "Teacher's Batch-Vault"
    # Use DATABASE_URL from environment if available (Rent/Prod), else fallback to SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./batchvault.db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    STATIC_PDF_DIR: str = "pdfs"

settings = Settings()

# --- Database Setup ---
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
