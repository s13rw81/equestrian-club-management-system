import random

import pytest
from faker import Faker

from data.db import convert_to_object_id
from tests.conftest import TEST_USER_EMAIL, client

fake = Faker()


def get_headers(token):
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


def get_truck_details():
    return {
        "registration_number": fake.license_plate(),
        "truck_type": fake.pystr(),
        "capacity": f"{fake.numerify('%%')}{fake.random_uppercase_letter()}",
        "special_features": fake.bs(),
        "gps_equipped": fake.pybool(),
        "air_conditioning": fake.pybool(),
        "name": fake.word(),
        # "availability": random.choice(["available", "un_available"]),
        "location": {"lat": str(fake.latitude()), "long": str(fake.longitude())},
        "driver": {"name": fake.name(), "phone_no": fake.phone_number()},
    }


def add_truck(access_token):
    route = "/logistic-company/trucks/add-truck"

    headers = get_headers(token=access_token)

    request_body = get_truck_details()

    response = client.post(url=route, json=request_body, headers=headers)

    assert response.status_code == 200

    return response.json()["truck_id"]


@pytest.fixture(scope="class")
def verify_logistics_company(get_database_connection):
    logistics_company_collection = get_database_connection["logistic_company"]
    logistics_company_collection.update_many(
        filter={}, update={"$set": {"is_khayyal_verified": True}}
    )


@pytest.fixture(scope="class")
def company_details():
    return {
        "email_address": TEST_USER_EMAIL,
        "phone_no": fake.phone_number(),
        "name": fake.company(),
        "description": fake.bs(),
    }


@pytest.fixture(scope="class")
def truck_details():
    return get_truck_details()


@pytest.fixture(scope="class")
def onboard_logistics_company(
    request, company_details, get_access_token_otp_verified, get_database_connection
):
    route_url = "/onboarding/create-logistic-company"

    headers = get_headers(token=get_access_token_otp_verified)

    request_body = {
        "email_address": company_details["email_address"],
        "phone_no": company_details["phone_no"],
        "name": company_details["name"],
        "description": company_details["description"],
    }

    response = client.post(route_url, headers=headers, json=request_body)

    assert response.status_code == 200

    logistic_company_id = response.json()["logistic_company_id"]

    yield logistic_company_id, get_access_token_otp_verified

    def cleanup_onboarded_logistics_company():
        logistics_company_collection = get_database_connection["logistic_company"]
        response = logistics_company_collection.delete_one(
            filter={"_id": convert_to_object_id(logistic_company_id)}
        )
        assert response.acknowledged
        assert response.deleted_count == 1

        trucks_collection = get_database_connection["trucks"]
        response = trucks_collection.delete_many(filter={})

        assert response.acknowledged
        assert response.deleted_count > 0

    def cleanup_user():
        users_collection = get_database_connection["users"]
        response = users_collection.delete_one(
            filter={"email_address": TEST_USER_EMAIL}
        )
        assert response.acknowledged
        assert response.deleted_count == 1

    request.addfinalizer(cleanup_user)
    request.addfinalizer(cleanup_onboarded_logistics_company)


@pytest.fixture(scope="class")
def add_trucks(
    request,
    onboard_logistics_company,
    verify_logistics_company,
):
    logistics_company_id, access_token = (
        onboard_logistics_company[0],
        onboard_logistics_company[1],
    )

    truck_id_1 = add_truck(access_token=access_token)
    truck_id_2 = add_truck(access_token=access_token)

    return [truck_id_1, truck_id_2]
