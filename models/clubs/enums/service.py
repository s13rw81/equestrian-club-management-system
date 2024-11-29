from enum import Enum


class ServiceType(Enum):
    TRAINING = "TRAINING"
    STABLING = "STABLING"


class SubServices(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    PACKAGE = "PACKAGE"


class ServiceStatus(Enum):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
