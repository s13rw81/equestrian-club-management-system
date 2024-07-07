import pytest
from data.db import convert_to_object_id
from tests.conftest import client, TEST_USER_EMAIL, TEST_USER_EMAIL_2

HORSE_SELL_DETAILS = {
    "name": "A name of the horse",
    "year_of_birth": "2069",
    "breed": "top class horse breed",
    "size": "size of the horse",
    "gender": "male",
    "description": "a description of the horse",
    "price": "1000 SAR"
}

HORSE_SELL_ENQUIRY_DETAILS = {
    "message": "this is an enquiry message"
}

common_data_dict = {}


@pytest.mark.horse_buy_sell_rent
class TestHorseBuySellFlow:

    @pytest.mark.dependency
    def test_enlist_horse_for_sell(self, get_access_token_otp_verified, get_database_connection):
        route_url = "/user/horses/enlist-for-sell"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        request_body = {
            "name": HORSE_SELL_DETAILS["name"],
            "year_of_birth": HORSE_SELL_DETAILS["year_of_birth"],
            "breed": HORSE_SELL_DETAILS["breed"],
            "size": HORSE_SELL_DETAILS["size"],
            "gender": HORSE_SELL_DETAILS["gender"],
            "description": HORSE_SELL_DETAILS["description"],
            "price": HORSE_SELL_DETAILS["price"]
        }

        response = client.post(route_url, headers=headers, json=request_body)

        assert response.status_code == 200

        horse_selling_service_id = response.json()["horse_selling_service_id"]

        horses_collection = get_database_connection["horses"]

        horse_selling_service_collection = get_database_connection["horse_selling_service"]

        horse_selling_service = horse_selling_service_collection.find_one(
            {"_id": convert_to_object_id(horse_selling_service_id)}
        )

        assert horse_selling_service is not None

        horse = horses_collection.find_one(
            {"_id": convert_to_object_id(horse_selling_service["horse_id"])}
        )

        assert horse is not None

        users_collection = get_database_connection["users"]

        user = users_collection.find_one({"email_address": TEST_USER_EMAIL})

        assert horse["name"] == HORSE_SELL_DETAILS["name"]
        assert horse["year_of_birth"] == HORSE_SELL_DETAILS["year_of_birth"]
        assert horse["breed"] == HORSE_SELL_DETAILS["breed"]
        assert horse["size"] == HORSE_SELL_DETAILS["size"]
        assert horse["gender"] == HORSE_SELL_DETAILS["gender"]
        assert horse["description"] == HORSE_SELL_DETAILS["description"]
        assert horse["uploaded_by"]["uploaded_by_id"] == str(user["_id"])

        assert horse_selling_service["price"] == HORSE_SELL_DETAILS["price"]
        assert horse_selling_service["provider"]["provider_type"] == str(user["_id"])

        common_data_dict["horse_selling_service_id"] = horse_selling_service_id
        common_data_dict["horse_id"] = horse_selling_service["horse_id"]

    @pytest.mark.dependency(depends=["TestHorseBuySellFlow::test_enlist_horse_for_sell"])
    def test_horse_sell_upload_images(self, get_access_token_otp_verified):
        horse_selling_service_id = common_data_dict["horse_selling_service_id"]

        route_url = f"/user/horses/{horse_selling_service_id}/upload-images"

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

    @pytest.mark.dependency(depends=["TestHorseBuySellFlow::test_horse_sell_upload_images"])
    def test_get_horses_for_sell(self, get_access_token_otp_verified):
        # This test only tests for own_listing=True, write a separate test case for
        # own_listing=False to test for another case
        route_url = "/user/horses/get-horses-for-sell"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        query_params = {
            "own_listing": True
        }

        response = client.get(route_url, params=query_params, headers=headers)

        assert response.status_code == 200

        response_data = response.json()[0]

        assert response_data["horse_selling_service_id"] == common_data_dict["horse_selling_service_id"]
        assert response_data["horse_id"] == common_data_dict["horse_id"]
        assert response_data["name"] == HORSE_SELL_DETAILS["name"]
        assert response_data["year_of_birth"] == HORSE_SELL_DETAILS["year_of_birth"]
        assert response_data["breed"] == HORSE_SELL_DETAILS["breed"]
        assert response_data["size"] == HORSE_SELL_DETAILS["size"]
        assert response_data["gender"] == HORSE_SELL_DETAILS["gender"]
        assert response_data["description"] == HORSE_SELL_DETAILS["description"]
        assert len(response_data["image_urls"]) == 3
        assert response_data["price"] == HORSE_SELL_DETAILS["price"]

    @pytest.mark.dependency(depends=["TestHorseBuySellFlow::test_enlist_horse_for_sell"])
    def test_update_sell_listing(self, get_access_token_otp_verified, get_database_connection):
        horse_selling_service_id = common_data_dict["horse_selling_service_id"]

        route_url = f"/user/horses/update-sell-listing/{horse_selling_service_id}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified}"
        }

        request_data = {
            "name": "a new name for the horse"
        }

        response = client.put(route_url, headers=headers, json=request_data)

        assert response.json()["status"] == "OK"

        horses_collection = get_database_connection["horses"]

        horse = horses_collection.find_one(
            {"_id": convert_to_object_id(common_data_dict["horse_id"])}
        )

        assert horse is not None

        assert horse["name"] == request_data["name"]

        request_data = {
            "name": HORSE_SELL_DETAILS["name"]
        }

        response = client.put(route_url, headers=headers, json=request_data)

        assert response.json()["status"] == "OK"

        horse = horses_collection.find_one(
            {"_id": convert_to_object_id(common_data_dict["horse_id"])}
        )

        assert horse is not None

        assert horse["name"] == HORSE_SELL_DETAILS["name"]

    @pytest.mark.dependency(depends=["TestHorseBuySellFlow::test_enlist_horse_for_sell"])
    def test_enquire_for_a_horse_sell(self, get_access_token_otp_verified_2, get_database_connection):
        route_url = "/user/horses/enquire-for-a-horse-sell"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified_2}"
        }

        request_data = {
            "horse_selling_service_id": common_data_dict["horse_selling_service_id"],
            "message": HORSE_SELL_ENQUIRY_DETAILS["message"]
        }

        response = client.post(route_url, headers=headers, json=request_data)

        assert response.status_code == 200

        horse_selling_enquiry_id = response.json()["horse_selling_enquiry_id"]

        horse_selling_enquiry_collection = get_database_connection["horse_selling_enquiry"]

        horse_selling_enquiry = horse_selling_enquiry_collection.find_one(
            {"_id": convert_to_object_id(horse_selling_enquiry_id)}
        )

        assert horse_selling_enquiry is not None

        users_collection = get_database_connection["users"]

        user = users_collection.find_one(
            {"email_address": TEST_USER_EMAIL_2}
        )

        assert user is not None

        assert horse_selling_enquiry["user_id"] == str(user["_id"])
        assert horse_selling_enquiry["horse_selling_service_id"] == common_data_dict["horse_selling_service_id"]
        assert horse_selling_enquiry["message"] == HORSE_SELL_ENQUIRY_DETAILS["message"]

        common_data_dict["horse_selling_enquiry_id"] = horse_selling_enquiry_id

    @pytest.mark.dpendency(depnds=["TestHorseBuySellFlow::test_enquire_for_a_horse_sell"])
    def test_update_horse_sell_enquiry(self, get_access_token_otp_verified_2, get_database_connection):

        horse_selling_enquiry_id = common_data_dict["horse_selling_enquiry_id"]

        route_url = f"/user/horses/update-horse-sell-enquiry/{horse_selling_enquiry_id}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified_2}"
        }

        request_data = {
            "message": "a new updated message"
        }

        response = client.put(route_url, headers=headers, json=request_data)

        assert response.status_code == 200

        assert response.json()["status"] == "OK"

        horse_selling_enquiry_collection = get_database_connection["horse_selling_enquiry"]

        horse_selling_enquiry = horse_selling_enquiry_collection.find_one(
            {"_id": convert_to_object_id(horse_selling_enquiry_id)}
        )

        assert horse_selling_enquiry is not None

        assert horse_selling_enquiry["message"] == request_data["message"]

        request_data = {
            "message": HORSE_SELL_ENQUIRY_DETAILS["message"]
        }

        response = client.put(route_url, headers=headers, json=request_data)

        assert response.status_code == 200

        assert response.json()["status"] == "OK"

        horse_selling_enquiry = horse_selling_enquiry_collection.find_one(
            {"_id": convert_to_object_id(horse_selling_enquiry_id)}
        )

        assert horse_selling_enquiry is not None

        assert horse_selling_enquiry["message"] == HORSE_SELL_ENQUIRY_DETAILS["message"]

    @pytest.mark.dependency(depends=["TestHorseBuySellFlow::test_enquire_for_a_horse_sell"])
    def test_get_horse_sell_enquiries(self, get_access_token_otp_verified_2):
        route_url = "/user/horses/get-horse-sell-enquiries"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {get_access_token_otp_verified_2}"
        }

        response = client.get(route_url, headers=headers)

        assert response.stats_code == 200

        horse_sell_enquiry = response.json()[0]

        assert horse_sell_enquiry["message"] == HORSE_SELL_ENQUIRY_DETAILS["message"]
        assert horse_sell_enquiry["horse_selling_service_id"] == common_data_dict["horse_selling_service_id"]
        assert horse_sell_enquiry["horse_selling_enquiry_id"] == common_data_dict["horse_selling_enquiry_id"]



