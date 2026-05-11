from sqlalchemy import create_engine       
from sqlalchemy.orm import sessionmaker    
from app.config import DATABASE_URL
from app.db.models import Base


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    """Creates all tables in Postgres if they don't already exist."""
    Base.metadata.create_all(bind=engine)
