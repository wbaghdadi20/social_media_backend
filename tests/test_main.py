from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_read_root(client: TestClient, db_session: Session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Social Media Backend API"}

def test_get_instance(client: TestClient, db_session: Session):
    response = client.get("/instance")
    assert response.status_code == 200
    # not sure how to actually test this