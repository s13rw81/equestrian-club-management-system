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
def get_database_connection():
    yield get_database()


@pytest.fixture(scope="class")
def get_access_token_not_otp_verified(get_users_database_collection):
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


@pytest.fixture(scope="class")
def get_access_token_otp_verified(get_access_token_not_otp_verified, get_users_database_collection):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {get_access_token_not_otp_verified}"
    }

    response = client.post("/auth/generate-sign-up-otp", headers=headers)

    assert response.status_code == 200

    user_dict = get_users_database_collection.find_one({"email_address": TEST_USER_EMAIL})

    assert not user_dict["otp_verified"]

    otp = user_dict["sign_up_verification_otp"]["otp"]

    params = {
        "user_provided_otp": otp
    }

    response = client.post("/auth/verify-sign-up-otp", params=params, headers=headers)

    assert response.status_code == 200

    user_dict = get_users_database_collection.find_one({"email_address": TEST_USER_EMAIL})

    assert user_dict["otp_verified"]

    yield get_access_token_not_otp_verified
