from fastapi.testclient import TestClient
from app.main import app  
from app.crud import create_user, get_user
from app.models import User
from app.schemas import UserCreate
from app.auth import delete_user
import uuid

client = TestClient(app) 

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_register_user():
    unique_email = f"test_{uuid.uuid4()}@example.com"
    user_data = UserCreate(email=unique_email, password="testpassword")
    response = client.post("/users/", json=user_data.model_dump())
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    # Clean queue
    user = get_user(unique_email)
    if user:
        delete_user(unique_email)

def test_login_for_access_token():
    unique_email = f"test_{uuid.uuid4()}@example.com"
    user_data = UserCreate(email=unique_email, password="testpassword")
    client.post("/users/", json=user_data.model_dump())

    response = client.post("/token", data={"username": unique_email, "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    user = get_user(unique_email)
    if user:
        delete_user(unique_email)

def test_read_users_me():
    unique_email = f"test_{uuid.uuid4()}@example.com"
    user_data = UserCreate(email=unique_email, password="testpassword")
    client.post("/users/", json=user_data.model_dump())

    # Get access token
    response = client.post("/token", data={"username": unique_email, "password": "testpassword"})
    access_token = response.json()["access_token"]

    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == unique_email
 
    user = get_user(unique_email)
    if user:
        delete_user(unique_email)

def test_invalid_login():
    response = client.post("/token", data={"username": "invalid@example.com", "password": "invalidpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect email or password"}

def test_unauthorized_access():
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
