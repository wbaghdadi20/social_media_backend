# import pytest
# from sqlalchemy.orm import Session
# from app.models import User
# from app.services.user_service import verify_password

# @pytest.mark.parametrize(
#     "user_data",
#     [
#         {"username": "testuser1", "email": "test1@example.com", "password": "password123"},
#         {"username": "testuser2", "email": "test2@example.com", "password": "password456"},
#     ]
# )
# def test_create_valid_user(client, transactional_db_session: Session, user_data):
#     response = client.post("/users/signup", json=user_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert data["token_type"] == "bearer"

#     user_in_db = transactional_db_session.query(User).filter(User.email == user_data["email"]).first()
#     assert user_in_db is not None
#     assert verify_password(user_data["password"], user_in_db.password) is True

# def test_create_user_duplicate_email(client, transactional_db_session: Session):
#     user_data = {"username": "uniqueuser1", "email": "duplicate@example.com", "password": "password123"}
#     response = client.post("/users/signup", json=user_data)
#     assert response.status_code == 200

#     user_data_dup = {"username": "uniqueuser2", "email": "duplicate@example.com", "password": "password456"}
#     response_dup = client.post("/users/signup", json=user_data_dup)
#     assert response_dup.status_code == 409
#     data_dup = response_dup.json()
#     assert data_dup["detail"] == "Email is already registered"

# def test_create_user_duplicate_username(client, transactional_db_session: Session):
#     user_data = {"username": "duplicateuser", "email": "unique1@example.com", "password": "password123"}
#     response = client.post("/users/signup", json=user_data)
#     assert response.status_code == 200

#     user_data_dup = {"username": "duplicateuser", "email": "unique2@example.com", "password": "password456"}
#     response_dup = client.post("/users/signup", json=user_data_dup)
#     assert response_dup.status_code == 409
#     data_dup = response_dup.json()
#     assert data_dup["detail"] == "Username is already registered"

# @pytest.mark.parametrize(
#     "user_data",
#     [
#         {"username": "user3", "email": "invalidemail", "password": "password123"},
#         {"username": "user4", "email": "user4@example.com", "password": "short"},
#         {"username": "ab", "email": "user5@example.com", "password": "password123"},
#     ]
# )
# def test_create_invalid_user(client, transactional_db_session: Session, user_data):
#     response = client.post("/users/signup", json=user_data)
#     assert response.status_code == 422
#     data = response.json()
#     assert "detail" in data

# def test_access_me_endpoint_logged_in(client, transactional_db_session: Session):
#     user_data = {"username": "testuser_me", "email": "test_me@example.com", "password": "password123"}
#     signup_response = client.post("/users/signup", json=user_data)
#     assert signup_response.status_code == 200
#     token = signup_response.json()["access_token"]

#     response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["username"] == user_data["username"]
#     assert data["email"] == user_data["email"]

# def test_access_me_endpoint_not_logged_in(client):
#     response = client.get("/users/me")
#     assert response.status_code == 403
#     data = response.json()
#     assert data["detail"] == "Not authenticated"

# def test_access_me_endpoint_invalid_token(client):
#     invalid_token = "thisis.an.invalidtoken"
#     response = client.get("/users/me", headers={"Authorization": f"Bearer {invalid_token}"})
#     assert response.status_code == 401
#     data = response.json()
#     assert data["detail"] == "Could not validate credentials"

# def test_access_me_endpoint_non_existing_user(client, transactional_db_session: Session):
#     from app.config.token import create_access_token
#     import uuid

#     fake_user_data = {
#         "id": str(uuid.uuid4()),
#         "username": "fakeuser",
#         "email": "fakeuser@example.com"
#     }
#     token = create_access_token(data=fake_user_data)

#     response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 401
#     data = response.json()
#     assert data["detail"] == "Could not validate credentials"