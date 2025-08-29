import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Format: postgresql+driver://user:password@host:port/database
user = 'postgres'
password = 'dhukka7860'
host = 'localhost'
database = 'options_market_db'

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,            # Log SQL statements (set False in prod)
    pool_size=10,         # Number of connections in pool
    max_overflow=20,      # Extra connections beyond pool_size
    pool_timeout=30,      # Timeout for getting connection
    pool_recycle=1800     # Recycle connections (seconds)
)

# Create session factory
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

