from enum import Enum


# TODO : update all transfer status
class TransferStatus(Enum):
    CREATED = "created"
    CANCELLED = "cancelled"
    PICK_UP_CONFIRMED = "pick_up_confirmed"
    IN_TRANSIT = "in_transit"


class TransferStatusPriority(Enum):
    CREATED = 1
    CANCELLED = 2
    PICK_UP_CONFIRMED = 3
    IN_TRANSIT = 4
