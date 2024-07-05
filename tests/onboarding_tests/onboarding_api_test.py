import pytest
from data.db import convert_to_object_id
from tests.conftest import client, TEST_USER_EMAIL

LOGISTIC_COMPANY_DETAILS = {
    "email_address": "someemail@domain.com",
    "phone_no": "+911111111111",
    "name": "name of the logistic-company",
    "description": "a description of the company"
}


@pytest.mark.onboarding
class TestOnboardingLogisticCompanyFlow:
    @pytest.mark.dependency
    def test_create_logistic_company(self, get_access_token_otp_verified, get_database_connection):
        route_url = "/onboarding/create-logistic-company"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        request_body = {
            "email_address": LOGISTIC_COMPANY_DETAILS["email_address"],
            "phone_no": LOGISTIC_COMPANY_DETAILS["phone_no"],
            "name": LOGISTIC_COMPANY_DETAILS["name"],
            "description": LOGISTIC_COMPANY_DETAILS["description"]
        }

        response = client.post(route_url, headers=headers, json=request_body)

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

        assert user["user_role"] == "LOGISTIC_COMPANY"

    @pytest.mark.dependency(depends=["TestOnboardingLogisticCompanyFlow::test_create_logistic_company"])
    def test_logistic_company_upload_images(self, get_access_token_otp_verified):
        route_url = "onboarding/logistic-company/upload-images"

        images_directory = "tests/test_images"

        headers = {
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        files = [
            ('images', ('space_image_1.jpg', open(f'{images_directory}/space_image_1.jpg', 'rb'), 'image/jpeg')),
            ('images', ('space_image_2.jpg', open(f'{images_directory}/space_image_2.jpg', 'rb'), 'image/jpeg')),
            ('images', ('space_image_3.jpg', open(f'{images_directory}/space_image_3.jpg', 'rb'), 'image/jpeg')),
        ]

        response = client.post(route_url, headers=headers, files=files)

        assert response.status_code == 200

        assert response.json()["status"] == "OK"

    @pytest.mark.dependency(depends=["TestOnboardingLogisticCompanyFlow::test_logistic_company_upload_images"])
    def test_get_logistic_company(self, get_access_token_otp_verified):
        route_url = "/onboarding/get-logistic-company"

        headers = {
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        response = client.get(route_url, headers=headers)

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["email_address"] == LOGISTIC_COMPANY_DETAILS["email_address"]
        assert response_data["phone_no"] == LOGISTIC_COMPANY_DETAILS["phone_no"]
        assert response_data["name"] == LOGISTIC_COMPANY_DETAILS["name"]
        assert response_data["description"] == LOGISTIC_COMPANY_DETAILS["description"]
        assert not response_data["is_khayyal_verified"]
        assert len(response_data["image_urls"]) == 3

