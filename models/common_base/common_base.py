from pydantic import BaseModel, field_serializer, field_validator, Field
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
    id: UUID = Field(default_factory=uuid4)
    created_on: datetime = Field(default_factory=lambda: datetime.now(pytz.utc))
    last_updated_on: datetime = Field(default_factory=lambda: datetime.now(pytz.utc))
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

    @field_validator(
        "created_on",
        "last_updated_on"
    )
    def add_tzinfo_to_datetime_objects(cls, datetime_object):
        if not datetime_object:
            return datetime_object

        return datetime_object.replace(tzinfo=pytz.utc)