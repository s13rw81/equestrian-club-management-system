from pydantic import BaseModel
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
    id: str = uuid4().hex
    created_on: datetime = datetime.now(pytz.utc)
    last_updated_on: datetime = datetime.now(pytz.utc)
    created_by: Optional[UUID] = None
    last_updated_by: Optional[UUID] = None
    deleted_on: Optional[datetime] = None