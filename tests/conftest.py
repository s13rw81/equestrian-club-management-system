from fastapi.testclient import TestClient
import pytest
from data.db import get_database
from main import app

client = TestClient(app)

TEST_USER_EMAIL = "test@test.com"
TEST_USER_EMAIL_2 = "test2@test.com"


class HelperFunctions:
    @staticmethod
    def create_an_otp_not_verified_user(user_email=TEST_USER_EMAIL):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "full_name": "Test User",
            "email_address": user_email,
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
            "username": user_email,
            "password": "111111"
        }

        response = client.post("/auth/token", headers=headers, data=data)

        assert response.status_code == 200

        access_token = response.json()["access_token"]
        return access_token

    @staticmethod
    def create_an_otp_verified_user(user_email=TEST_USER_EMAIL):
        not_otp_verified_user_token = HelperFunctions.create_an_otp_not_verified_user(user_email=user_email)

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {not_otp_verified_user_token}"
        }

        response = client.post("/auth/generate-sign-up-otp", headers=headers)

        assert response.status_code == 200

        user_dict = get_users_database_collection.find_one({"email_address": user_email})

        assert not user_dict["otp_verified"]

        otp = user_dict["sign_up_verification_otp"]["otp"]

        params = {
            "user_provided_otp": otp
        }

        response = client.post("/auth/verify-sign-up-otp", params=params, headers=headers)

        assert response.status_code == 200

        user_dict = get_users_database_collection.find_one({"email_address": user_email})

        assert user_dict["otp_verified"]

        return user_email

    @staticmethod
    def get_database_connection():
        return get_database()


@pytest.fixture(scope="class")
def get_users_database_collection():
    yield get_database()["users"]


@pytest.fixture(scope="class")
def get_database_connection():
    yield HelperFunctions.get_database_connection()


@pytest.fixture(scope="class")
def get_access_token_not_otp_verified():
    access_token = HelperFunctions.create_an_otp_not_verified_user(user_email=TEST_USER_EMAIL)

    yield access_token


@pytest.fixture(scope="class")
def get_access_token_otp_verified():
    access_token = HelperFunctions.create_an_otp_verified_user(user_email=TEST_USER_EMAIL)

    yield access_token


@pytest.fixture(scope="class")
def get_access_token_otp_verified_2():
    access_token = HelperFunctions.create_an_otp_verified_user(user_email=TEST_USER_EMAIL_2)

    yield access_token
