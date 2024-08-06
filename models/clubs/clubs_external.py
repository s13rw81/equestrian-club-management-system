from typing import Optional, List

from models.club_services_generic_activity.generic_activity_service_model import GenericActivityService
from models.club_services_horse_shoeing.horse_shoeing_service_model import HorseShoeingService
from models.services_riding_lession.riding_lesson_service_model import RidingLessonService
from models.trainer.trainer import TrainerInternalWithID, TrainerSlim
from pydantic import BaseModel


class ClubExternal(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str]
    image_urls: Optional[List[str]]
    average_rating: Optional[float]

    # detailed club
    is_khayyal_verified: Optional[bool] = None
    riding_lesson_service: Optional[RidingLessonService] = None
    horse_shoeing_service: Optional[HorseShoeingService] = None
    generic_activity_service: Optional[GenericActivityService] = None
    trainers: Optional[List[TrainerSlim]] = None
