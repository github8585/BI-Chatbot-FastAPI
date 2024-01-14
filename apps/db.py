import psycopg2
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace these variables with your actual database credentials
db_username = 'username'
db_password = 'password'
db_host = 'host'  # e.g., 'localhost' or the actual IP address
db_name = 'database_name' 

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
