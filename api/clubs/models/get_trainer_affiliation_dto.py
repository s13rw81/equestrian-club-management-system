from pydantic import BaseModel, field_serializer
from uuid import UUID


class GetTrainerAffiliationDTO(BaseModel):
    id: UUID
    club_id: str
    full_name: str
    email_address: str
    phone_number: str

    @field_serializer("id")
    @field_serializer("id")
    def serialize_uuids(self, value):
        if not value:
            return

        return str(value)