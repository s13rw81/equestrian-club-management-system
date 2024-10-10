from pydantic import BaseModel, field_serializer
from uuid import UUID, uuid4
from datetime import datetime
import pytz
from typing import Optional


# this class represents the common fields which are present across
# all the collections in the database
# all the models that represents the data structure of a document
# in a collection, e.g. ClubInternal (generally AnythingInternal)
# should inherit from this base class
class CommonBase(BaseModel):
    id: UUID = uuid4()
    created_on: datetime = datetime.now(pytz.utc)
    last_updated_on: datetime = datetime.now(pytz.utc)
    created_by: Optional[UUID] = None
    last_updated_by: Optional[UUID] = None
    deleted_on: Optional[datetime] = None

    @field_serializer(
        "id",
        "created_by",
        "last_updated_by",

    )
    def serialize_uuids(self, value):
        if not value:
            return

        return str(value)
