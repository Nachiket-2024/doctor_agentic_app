# --- Import necessary SQLAlchemy components ---
from sqlalchemy.orm import sessionmaker
from .database import engine

# --- Create a configured "Session" class ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
