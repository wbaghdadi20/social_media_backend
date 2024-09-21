# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine, StaticPool
# from sqlalchemy.orm import sessionmaker
# from app.main import app
# from app.config.database import get_db

# TEST_DATABASE_URL = "sqlite:///:memory:"

# client = TestClient(app)

# engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def override_get_db():
#     print("db dependency override")
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.config.database import get_db
import app.models as models

# Define the test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create the engine for the test database
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create a configured "Session" class
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    print("db_engine")
    """Fixture to provide the test database engine."""
    return engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    print("db_session")
    """Fixture to provide a SQLAlchemy session for tests."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# If you have tests that require the TestClient, you can include it here
@pytest.fixture(scope="module")
def client():
    print("client")
    """
    Fixture to provide a TestClient with dependency overrides.
    Useful for integration tests involving routes/endpoints.
    """
    # Override the get_db dependency
    def override_get_db():
        print("Override get db")
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_db, None)