import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def _load_dotenv() -> None:
    """Load key=value pairs from the workspace .env into process env."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

# Format: postgresql+driver://user:password@host:port/database
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PWD")
host = os.getenv("POSTGRES_HOST", "localhost")
database = os.getenv("POSTGRES_DB", "options_market_db")
port = os.getenv("POSTGRES_PORT", "5432")

if not password:
    raise RuntimeError(
        "Missing POSTGRES_PWD. Set it in environment or .env at workspace root."
    )

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Log SQL statements (set False in prod)
    pool_size=10,  # Number of connections in pool
    max_overflow=20,  # Extra connections beyond pool_size
    pool_timeout=30,  # Timeout for getting connection
    pool_recycle=1800,  # Recycle connections (seconds)
)

# Create session factory
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_pgconn():
    try:
        with Session() as session:
            result = session.execute(text("SELECT 1"))
            print("Postgres Connection Succesful!")
            return True
    except Exception as e:
        print("Postgres Connection Failed...")
        raise e
