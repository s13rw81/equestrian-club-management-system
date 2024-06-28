from fastapi.testclient import TestClient
from main import app

client = TestClient(app)



def test_user_signup_flow():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "full_name": "Test User",
        "email_address": "test@test.com",
        "password": "111111",
        "riding_stage": "BEGINNER",
        "horse_ownership_status": "YES",
        "equestrian_discipline": "RIDING_HORSE"
    }

    response = client.post("/user/signup", headers=headers, json=data)

    assert response.status_code == 200

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "",
        "username": "test@test.com",
        "password": "111111",
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }

    response = client.post("/auth/token", headers=headers, json=data)

