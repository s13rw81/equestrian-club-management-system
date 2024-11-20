from enum import Enum


class ServiceType(Enum):
    TRAINING = "training"
    STABLING = "stabling"


class SubServices(Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"
    PACKAGE = "package"


class ServiceStatus(Enum):
    ENABLE = "enable"
    DISABLE = "disable"
