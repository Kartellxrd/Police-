import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environmental variables from your secure backend/.env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ CRITICAL ERROR: DATABASE_URL is missing from the backend/.env file!")

# The engine handles the persistent network connection pool to Supabase
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Keeps 10 open connections ready to use immediately
    max_overflow=20,     # Can temporarily spin up 20 extra channels if traffic spikes
    pool_pre_ping=True   # Double-checks if a connection is alive before trying to use it
)

# Individual database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our relational database tables will inherit from
Base = declarative_base()

# Dependency injector to yield clean, isolated database sessions per API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Always close the connection pooler channel when the API call ends