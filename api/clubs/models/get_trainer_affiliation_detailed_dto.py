from . import GetTrainerAffiliationDTO, GetClubDTO
from typing import Optional

class GetTrainerAffiliationDetailedDTO(GetTrainerAffiliationDTO):
    club: Optional[GetClubDTO] = None