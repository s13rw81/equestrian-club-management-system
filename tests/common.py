from fastapi.testclient import TestClient
import pytest
from data.db import get_database
from main import app

client = TestClient(app)

TEST_USER_EMAIL = "test@test.com"


@pytest.fixture(scope="class")
def get_users_database_collection():
    yield get_database()["users"]


@pytest.fixture(scope="class")
def get_access_token(get_users_database_collection):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "full_name": "Test User",
        "email_address": TEST_USER_EMAIL,
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
        "username": TEST_USER_EMAIL,
        "password": "111111"
    }

    response = client.post("/auth/token", headers=headers, data=data)

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    yield access_token

    result = get_users_database_collection.delete_one({"email_address": TEST_USER_EMAIL})

    assert result.deleted_count == 1
