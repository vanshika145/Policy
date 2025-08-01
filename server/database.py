from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - you'll need to set this in your .env file
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./test.db"  # Fallback to SQLite for development
)

# Try to create engine, fallback to SQLite if PostgreSQL not available
try:
    engine = create_engine(DATABASE_URL)
    print("Database engine created successfully")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    print("   Falling back to SQLite for development")
    # Use SQLite as fallback
    engine = create_engine("sqlite:///./test.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 