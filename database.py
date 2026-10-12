import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# We use an environment variable to toggle between MySQL (production) and SQLite (testing)
# By default, we use SQLite so your app doesn't crash if MySQL isn't running on your laptop.
# To use MySQL for the final demo, set your environment variable: 
# DATABASE_URL="mysql+pymysql://root:password@localhost/sih2026"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sih_hackathon.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread=False for FastAPI concurrency
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
