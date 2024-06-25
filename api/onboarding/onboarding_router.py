from fastapi import APIRouter

onboarding_api_router = APIRouter(
    prefix = "/onboard",
    tags = ["onboarding"]
)
