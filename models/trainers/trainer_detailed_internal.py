from . import TrainerInternal
from models.trainer_certification import TrainerCertificationInternal
from models.trainer_specialization import TrainerSpecializationInternal
from models.generic_get_query_with_pagination import Lookup
from typing import Annotated

class TrainerDetailedInternal(TrainerInternal):
    certifications: Annotated[
        list[TrainerCertificationInternal],
        Lookup(
            from_collection="trainer_certifications",
            local_field="id",
            foreign_field="trainer_id",
            as_key_name="certifications",
            is_one_to_one=False
        )
    ] = []
    specializations: Annotated[
        list[TrainerSpecializationInternal],
        Lookup(
            from_collection="trainer_specializations",
            local_field="id",
            foreign_field="trainer_id",
            as_key_name="specializations",
            is_one_to_one=False
        )
    ] = []