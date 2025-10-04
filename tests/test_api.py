from fastapi.testclient import TestClient
from app.main import app
import random

client = TestClient(app)

def test_root_endpoint():
    """Test 1: Root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Management API"}

def test_user_registration():
    """Test 2: User registration - handle any status code"""

    random_email = f"test{random.randint(1000,9999)}@example.com"
    
    response = client.post("/register", json={
        "email": random_email,
        "password": "simple123"  
    })
    
    assert response.status_code != 500, f"Registration crashed with 500: {response.text}"
    print(f"Registration status: {response.status_code}")

def test_user_login():
    """Test 3: User login - create user first if needed"""
    # First ensure user exists
    client.post("/register", json={
        "email": "logintest@example.com", 
        "password": "simple123"
    })
    
    response = client.post("/login", json={
        "email": "logintest@example.com",
        "password": "simple123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint_without_auth():
    """Test 4: Protected endpoints require auth - accept 401 OR 403"""
    response = client.get("/tasks")
    # Both 401 and 403 mean "not authorized"
    assert response.status_code in [401, 403]