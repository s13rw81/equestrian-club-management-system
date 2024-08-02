from typing import Optional

from api.onboarding.models import Location, RidingLessonService, GenericActivityService, HorseShoeingService
from pydantic import BaseModel


class UpdateClubRequest(BaseModel):
    email_address: Optional[str] = None
    address: Optional[str] = None
    phone_no: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Location] = None
    riding_lesson_service: Optional[RidingLessonService] = None
    horse_shoeing_service: Optional[HorseShoeingService] = None
    generic_activity_service: Optional[GenericActivityService] = None
