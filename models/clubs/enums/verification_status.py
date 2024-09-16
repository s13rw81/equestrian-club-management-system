from enum import Enum

class VerificationStatus(Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"