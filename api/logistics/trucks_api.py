"""
it is understood that Admin i.e the Truck company
already has signed up. So we would by default have a company_collection
available with us.
we need a truck collection.
company_collection will have a reference field 
"""

from fastapi import APIRouter

trucks_api_router = APIRouter(prefix="/trucks", tags=["logistics"])


@trucks_api_router.get("")
def get_trucks_list():
    return {"status": "ok"}
