from data.db import PyObjectId
from models.logistics_company_services import Provider
from pydantic import BaseModel


class GenericActivityService(BaseModel):
    price: int
    provider: Provider

    class Config:
        json_encoders = {
            PyObjectId: lambda v: str(v)  # Custom encoder for PyObjectId
        }
