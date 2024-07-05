import pytest
from data.db import convert_to_object_id
from tests.conftest import client, TEST_USER_EMAIL


@pytest.mark.onboarding
class TestOnboardingLogisticCompanyFlow:
    @pytest.mark.dependency
    def test_create_logistic_company(self, get_access_token_otp_verified, get_database_connection):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        request_body = {
            "email_address": "someemail@domain.com",
            "phone_no": "+911111111111",
            "name": "name of the logistic-company",
            "description": "a description of the company"
        }

        response = client.post("/onboarding/create-logistic-company", headers=headers, json=request_body)

        assert response.status_code == 200

        logistic_company_id = response.json()["logistic_company_id"]

        logistic_company_collection = get_database_connection["logistic_company"]

        logistic_company = logistic_company_collection.find_one(
            {"_id": convert_to_object_id(logistic_company_id)}
        )

        users_collection = get_database_connection["users"]

        user = users_collection.find_one({"email_address": TEST_USER_EMAIL})

        assert logistic_company["email_address"] == request_body["email_address"]

        assert logistic_company["phone_no"] == request_body["phone_no"]

        assert logistic_company["name"] == request_body["name"]

        assert logistic_company["description"] == request_body["description"]

        assert not logistic_company["is_khayyal_verified"]

        assert logistic_company["users"][0]["user_id"] == str(user["_id"])
