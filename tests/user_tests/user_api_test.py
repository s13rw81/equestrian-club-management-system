import pytest
from fastapi.testclient import TestClient
from main import app
from data.db import get_users_collection

client = TestClient(app)

TEST_USER_EMAIL = "test@test.com"


@pytest.fixture(scope="class")
def get_users_database_collection():
    yield get_users_collection()


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


class TestUserFlow:
    @pytest.mark.dependency()
    def test_generate_otp(self, get_access_token):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token}"
        }

        response = client.post("/auth/generate-sign-up-otp", headers=headers)

        assert response.status_code == 200

    @pytest.mark.dependency(depends=["TestUserFlow::test_generate_otp"])
    def test_verify_otp(self, get_access_token, get_users_database_collection):
        user_dict = get_users_database_collection.find_one({"email_address": TEST_USER_EMAIL})

        assert not user_dict["otp_verified"]

        otp = user_dict["sign_up_verification_otp"]["otp"]

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token}"
        }

        params = {
            "user_provided_otp": otp
        }

        response = client.post("/auth/verify-sign-up-otp", params=params, headers=headers)

        assert response.status_code == 200

        user_dict = get_users_database_collection.find_one({"email_address": TEST_USER_EMAIL})

        assert user_dict["otp_verified"]

    @pytest.mark.dependency()
    def test_reset_password_request(self):
        headers = {
            "accept": "application/json"
        }

        params = {
            "email_address": TEST_USER_EMAIL
        }

        response = client.post("/auth/reset-password-request", headers=headers, params=params)

        assert response.status_code == 200

    @pytest.mark.dependency(depends=["TestUserFlow::test_reset_password_request"])
    def test_rest_password_update_password(self, get_users_database_collection):
        user_dict = get_users_database_collection.find_one({"email_address": TEST_USER_EMAIL})

        otp = user_dict["password_reset_verification_otp"]["otp"]

        headers = {
            "accept": "application/json",
            "Content-type": "application/json"
        }

        data = {
            "email_address": TEST_USER_EMAIL,
            "otp": otp,
            "new_password": "string"
        }

        response = client.put("/auth/reset-password-update-password", headers=headers, json=data)

        assert response.status_code == 200

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "",
            "username": TEST_USER_EMAIL,
            "password": "string",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }

        response = client.post("/auth/token", headers=headers, data=data)

        assert response.status_code == 200
