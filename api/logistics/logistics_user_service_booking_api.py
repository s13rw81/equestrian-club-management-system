from fastapi import APIRouter

from data.db import get_truck_collection
from logic.logistics.haversine import haversine

service_booking_router = APIRouter(tags=["logistics-consumer-apis"])


trucks_collection = get_truck_collection()


@service_booking_router.get("/find-nearby-trucks")
def find_nearby_trucks(radius: float, lat: float, long: float):

    trucks = trucks_collection.find({}, {})

    trucks_within_radius = []

    for truck in trucks:
        truck_lat = truck["location"]["lat"]
        truck_long = truck["location"]["long"]

        distance = haversine(lon1=long, lat1=lat, lon2=truck_long, lat2=truck_lat)
        if distance <= radius:
            trucks_within_radius.append(truck)
