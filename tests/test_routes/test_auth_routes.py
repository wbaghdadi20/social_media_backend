# import pytest
# from sqlalchemy.orm import Session

# @pytest.fixture(scope='function')
# def transactional_db_session(db_session: Session):
#     """
#     Fixture to create and rollback a transaction after each test case.
#     """
#     transaction = db_session.begin_nested()  # Start a nested transaction

#     yield db_session

#     transaction.rollback()  # Rollback after test case

# def test_login_existing_user(client, transactional_db_session: Session):
#     """
#     Test logging in with an existing user.
#     """
#     user_data = {"username": "testloginuser", "email": "testlogin@example.com", "password": "password123"}
#     signup_response = client.post("/users/signup", json=user_data)
#     assert signup_response.status_code == 200
    
#     login_data = {"username": "testloginuser", "email": "testlogin@example.com", "password": "password123"}
#     login_response = client.post("/auth/login", json=login_data)
#     assert login_response.status_code == 200
#     data = login_response.json()
#     assert "access_token" in data
#     assert data["token_type"] == "bearer"

# def test_login_non_existing_user(client, transactional_db_session: Session):
#     """
#     Test logging in with credentials that don't correspond to any user.
#     """
#     login_data = {"username": "nonexistentuser", "email": "nonexistent@example.com", "password": "password123"}
#     response = client.post("/auth/login", json=login_data)
#     assert response.status_code == 404
#     data = response.json()
#     assert data["detail"] == "User not found"

# def test_login_wrong_password(client, transactional_db_session: Session):
#     """
#     Test logging in with correct username and email but wrong password.
#     """
#     user_data = {"username": "testloginuser2", "email": "testlogin2@example.com", "password": "password123"}
#     signup_response = client.post("/users/signup", json=user_data)
#     assert signup_response.status_code == 200
    
#     login_data = {"username": "testloginuser2", "email": "testlogin2@example.com", "password": "wrongpassword"}
#     login_response = client.post("/auth/login", json=login_data)
#     assert login_response.status_code == 404
#     data = login_response.json()
#     assert data["detail"] == "User not found"

# @pytest.mark.parametrize(
#     "login_data",
#     [
#         {"email": "test1@example.com", "password": "password123"},
#         {"username": "user1", "password": "password123"},
#         {"username": "user1", "email": "test2@example.com"},
#         {"username": "user2", "email": "invalidemail", "password": "password123"},
#         {"username": "user3", "email": "test3@example.com", "password": "short"},
#     ]
# )
# def test_login_invalid_input(client, transactional_db_session: Session, login_data):
#     """
#     Test logging in with invalid input data.
#     """
#     response = client.post("/auth/login", json=login_data)
#     assert response.status_code == 422
#     data = response.json()
#     assert "detail" in data

# def test_login_existing_user_multiple_times(client, transactional_db_session: Session):
#     """
#     Test logging in multiple times with the same user to ensure consistent behavior.
#     """
#     user_data = {"username": "testloginuser3", "email": "testlogin3@example.com", "password": "password123"}
#     signup_response = client.post("/users/signup", json=user_data)
#     assert signup_response.status_code == 200
    
#     login_data = {"username": "testloginuser3", "email": "testlogin3@example.com", "password": "password123"}
#     for i in range(5):
#         login_response = client.post("/auth/login", json=login_data)
#         assert login_response.status_code == 200
#         data = login_response.json()
#         assert "access_token" in data

# def test_login_case_insensitive_email(client, transactional_db_session: Session):
#     """
#     Test that email login is case-sensitive or case-insensitive based on implementation.
#     """
#     user_data = {"username": "testloginuser4", "email": "testlogin4@example.com", "password": "password123"}
#     signup_response = client.post("/users/signup", json=user_data)
#     assert signup_response.status_code == 200
    
#     login_data = {"username": "testloginuser4", "email": "TestLogin4@Example.com", "password": "password123"}
#     login_response = client.post("/auth/login", json=login_data)
#     assert login_response.status_code == 404
#     data = login_response.json()
#     assert data["detail"] == "User not found"