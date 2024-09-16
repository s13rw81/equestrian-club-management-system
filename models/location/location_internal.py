from pydantic import BaseModel

# this will be used only as a nested field
# in AnythingInternal models it need not
# inherit from CommonBase
class LocationInternal(BaseModel):
    lat: str
    long: str