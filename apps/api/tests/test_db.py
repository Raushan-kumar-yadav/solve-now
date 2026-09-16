from sqlalchemy import create_engine
from core.config import settings

def test_database_connection():
    # Attempt to connect to the database
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    try:
        with engine.connect() as conn:
            assert conn is not None
    except Exception as e:
        assert False, f"Database connection failed: {e}"

