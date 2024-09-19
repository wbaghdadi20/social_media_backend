import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config.database import Base, get_db
from fastapi.testclient import TestClient
from app.main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope='session')
def engine():
    """
    Creates a new SQLAlchemy engine for the testing session.
    Uses an in-memory SQLite database.
    """
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope='session')
def BaseModel():
    """
    Provides the declarative base model for the session.
    """
    return Base

@pytest.fixture(scope='function')
def db_session(engine, BaseModel):
    """
    Creates a new database session for a test and ensures a clean state.
    - Creates all tables before the test.
    - Drops all tables after the test.
    - Enables foreign key constraints in SQLite.
    """
    # Create all tables
    BaseModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Enable foreign key constraints for SQLite
    session.execute(text('PRAGMA foreign_keys=ON'))

    yield session  # This is where the testing happens

    session.rollback()  # Rollback any changes made during the test
    session.close()
    # Drop all tables
    BaseModel.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def client(db_session: Session):
    """
    Create a TestClient with overridden dependencies to use the in-memory db_session.
    """
    # Define a dependency override
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override the get_db dependency in the app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Remove the dependency override after the test
    app.dependency_overrides.pop(get_db, None)