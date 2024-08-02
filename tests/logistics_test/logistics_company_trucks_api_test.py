import random

import pytest
from faker import Faker

from data.db import convert_to_object_id
from models.truck.trucks import TruckInternal
from tests.conftest import client
from tests.logistics_test.conftest import get_truck_details

fake = Faker()


def get_headers(token):
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


@pytest.mark.trucks
class TestLogisticsCompanyTrucks:

    @pytest.mark.dependency
    def test_add_truck(
        self,
        onboard_logistics_company,
        verify_logistics_company,
        get_database_connection,
        truck_details,
    ):
        logistics_company_id, access_token = (
            onboard_logistics_company[0],
            onboard_logistics_company[1],
        )
        route = "/logistic-company/trucks/add-truck"

        headers = get_headers(token=access_token)

        request_body = truck_details

        response = client.post(url=route, json=request_body, headers=headers)

        assert response.status_code == 200

        truck_id = response.json()["truck_id"]

        trucks_collection = get_database_connection["trucks"]
        truck = trucks_collection.find_one(
            filter={"_id": convert_to_object_id(truck_id)}
        )

        assert truck

        truck = TruckInternal(**truck)

        assert truck.registration_number == request_body["registration_number"]
        assert truck.truck_type == request_body["truck_type"]
        assert truck.capacity == request_body["capacity"]
        assert truck.special_features == request_body["special_features"]
        assert truck.gps_equipped == request_body["gps_equipped"]
        assert truck.air_conditioning == request_body["air_conditioning"]
        assert truck.name == request_body["name"]

        truck_details["truck_id"] = truck_id
        truck_details["logistics_company_id"] = logistics_company_id

    @pytest.mark.dependency(depends=["TestLogisticsCompanyTrucks::test_add_truck"])
    def test_upload_truck_images(
        self, onboard_logistics_company, get_database_connection, truck_details
    ):
        logistics_company_id, access_token = (
            onboard_logistics_company[0],
            onboard_logistics_company[1],
        )

        truck_id = truck_details["truck_id"]

        truck_collection = get_database_connection["trucks"]
        truck = truck_collection.find_one(
            filter={"_id": convert_to_object_id(truck_id)}
        )

        assert truck["images"] == []

        route = f"/logistic-company/trucks/upload-truck-images/{truck_id}"
        images_dir = "tests/test_images"

        headers = get_headers(token=access_token)

        files = [
            (
                "images",
                (
                    "space_image_1.jpg",
                    open(f"{images_dir}/space_image_1.jpg", "rb"),
                    "image/jpeg",
                ),
            ),
            (
                "images",
                (
                    "space_image_2.jpg",
                    open(f"{images_dir}/space_image_2.jpg", "rb"),
                    "image/jpeg",
                ),
            ),
            (
                "images",
                (
                    "space_image_3.jpg",
                    open(f"{images_dir}/space_image_3.jpg", "rb"),
                    "image/jpeg",
                ),
            ),
        ]

        response = client.post(url=route, headers=headers, files=files)
        print(f"upload_truck_images_response {response.json()}")

        assert response.status_code == 200
        assert response.json() == {"status": "OK"}

        truck = truck_collection.find_one(
            filter={"_id": convert_to_object_id(truck_id)}
        )
        assert truck["images"] != []

    @pytest.mark.dependency(
        depends=["TestLogisticsCompanyTrucks::test_upload_truck_images"]
    )
    def test_get_truck_by_id(self, onboard_logistics_company, truck_details):
        logistics_company_id, access_token = (
            onboard_logistics_company[0],
            onboard_logistics_company[1],
        )

        truck_id = truck_details["truck_id"]

        route = f"/logistic-company/trucks/get-truck/{truck_id}"
        headers = get_headers(token=access_token)

        response = client.get(url=route, headers=headers)

        assert response.status_code == 200

        response = response.json()

        required_return_attributes = [
            "logistics_company_id",
            "registration_number",
            "truck_type",
            "capacity",
            "special_features",
            "gps_equipped",
            "air_conditioning",
            "name",
            "driver",
            "location",
            "truck_id",
            "image_urls",
        ]

        for k, v in response.items():
            assert k in required_return_attributes
            if k == "image_urls":
                assert len(v) > 0
                continue

            if isinstance(v, dict):
                if k == "driver":
                    truck_details[k]["name"] == v["name"]
                    truck_details[k]["phone_no"] == v["phone_no"]
                elif k == "location":
                    truck_details[k]["lat"] == v["lat"]
                    truck_details[k]["long"] == v["long"]
                continue

            assert truck_details[k] == v

    @pytest.mark.dependency(
        depends=["TestLogisticsCompanyTrucks::test_get_truck_by_id"]
    )
    def test_get_trucks(
        self, onboard_logistics_company, truck_details, get_database_connection
    ):
        logistics_company_id, access_token = (
            onboard_logistics_company[0],
            onboard_logistics_company[1],
        )

        trucks_collection = get_database_connection["trucks"]
        temp_truck_data = get_truck_details()
        temp_truck_id = str(trucks_collection.insert_one(temp_truck_data).inserted_id)

        truck_ids = [truck_details["truck_id"], temp_truck_id]

        route = f"/logistic-company/trucks/get-truck"
        headers = get_headers(token=access_token)

        response = client.get(url=route, headers=headers)
        assert response.status_code == 200

        response = response.json()

        assert isinstance(response, list)

        required_return_attributes = [
            "logistics_company_id",
            "registration_number",
            "truck_type",
            "capacity",
            "special_features",
            "gps_equipped",
            "air_conditioning",
            "name",
            "truck_id",
            "location",
            "image_urls",
            "driver",
        ]

        for truck in response:
            test_data = {}
            if truck["truck_id"] == truck_details["truck_id"]:
                test_data = truck_details
            else:
                test_data = temp_truck_data

            assert test_data["truck_id"] in truck_ids

            for k, v in truck.items():
                assert k in required_return_attributes
                if k == "image_urls":
                    assert len(v) > 0
                    continue

                if isinstance(v, dict):
                    if k == "driver":
                        test_data[k]["name"] == v["name"]
                        test_data[k]["phone_no"] == v["phone_no"]
                    elif k == "location":
                        test_data[k]["lat"] == v["lat"]
                        test_data[k]["long"] == v["long"]
                    continue

                assert test_data[k] == v

    @pytest.mark.dependency(
        depends=["TestLogisticsCompanyTrucks::test_get_truck_by_id"]
    )
    @pytest.mark.parametrize(
        argnames="update_payload",
        argvalues=[
            get_truck_details(),
            dict(
                random.sample(
                    population=get_truck_details().items(), k=random.randint(a=1, b=4)
                )
            ),
            {},
            {"override": True},
        ],
    )
    def test_update_trucks(
        self,
        onboard_logistics_company,
        get_database_connection,
        truck_details,
        update_payload,
    ):
        logistics_company_id, access_token = (
            onboard_logistics_company[0],
            onboard_logistics_company[1],
        )

        truck_id = truck_details["truck_id"]

        route = f"/logistic-company/trucks/update-truck/{truck_id}"
        headers = get_headers(token=access_token)

        update_payload = {k: v for k, v in update_payload.items() if v}
        if update_payload.get("override"):
            update_payload = truck_details

        response = client.put(url=route, headers=headers, json=update_payload)

        assert response.status_code == 200
        assert response.json() == {"status": "OK"}

        trucks_collection = get_database_connection["trucks"]
        truck = trucks_collection.find_one(
            filter={"_id": convert_to_object_id(truck_id)}
        )

        assert truck

        for k, v in update_payload.items():
            if k == "truck_id":
                continue
            elif k == "driver":
                assert truck[k]["name"] == update_payload[k]["name"]
                assert truck[k]["phone_no"] == update_payload[k]["phone_no"]
                continue
            elif k == "location":
                assert str(truck[k]["lat"]) == update_payload[k]["lat"]
                assert str(truck[k]["long"]) == update_payload[k]["long"]
                continue

            assert truck[k] == v
