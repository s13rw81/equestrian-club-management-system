from pydantic import BaseModel, field_serializer, computed_field
from uuid import UUID


class GetTrainerAffiliationDTO(BaseModel):
    id: UUID
    club_id: str
    full_name: str
    email_address: str
    phone_number: str

    @computed_field
    @property
    def club_affiliation_number(self) -> str:
        return str(self.id)

    @field_serializer("id")
    def serialize_uuids(self, value):
        if not value:
            return

        return str(value)
