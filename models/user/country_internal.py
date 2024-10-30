from typing import Optional, Union
from pydantic import BaseModel, field_serializer
from ..common_base import CommonBase
from .enums import MiddleEastCountries


class CountryInternal(CommonBase):
    country_name: Union[str, MiddleEastCountries]  # Accepts either a string or an enum
    country_code: str
    country_iso: Optional[str] = None

    @field_serializer("country_name")
    def enum_serializer(self, country_name):
        if isinstance(country_name, MiddleEastCountries):
            return country_name.value
        return country_name
