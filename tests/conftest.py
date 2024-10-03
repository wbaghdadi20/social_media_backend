import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
import app.models as models
from app.schemas import UserCreate, Token
import app.services.auth_service as auth_service
from app.config.database import get_db
from app.config.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

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

@pytest.fixture(scope="function")
def client(db_session):
    print("client")
    print(SQLALCHEMY_DATABASE_URL)
    """
    Fixture to provide a TestClient with dependency overrides.
    Useful for integration tests involving routes/endpoints.
    """
    def override_get_db():
        print("Override get db")
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def existing_user(db_session: Session):
    """
    Fixture to pre-populate the db with a user
    """
    user_create = UserCreate(
        username="test_user",
        email="test_user@example.com",
        password="password123"
    )
    return auth_service.create_user(
        user_create=user_create,
        db=db_session
    )