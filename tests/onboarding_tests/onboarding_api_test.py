import pytest
from tests.conftest import client, TEST_USER_EMAIL


@pytest.mark.onboarding
class TestOnboardingLogisticCompanyFlow:
    @pytest.mark.dependency
    def test_create_logistic_company(self, get_access_token_not_otp_verified, get_database_connection):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_not_otp_verified}"
        }

        request_body = {
            "email_address": "someemail@domain.com",
            "phone_no": "+911111111111",
            "name": "name of the logistic-company",
            "description": "a description of the company"
        }

        response = client.post("/onboarding/create-logistic-company", headers=headers, json=request_body)

        assert response.status_code == 200
