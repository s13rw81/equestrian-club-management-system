from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from logging_config import log
from utils.image_management import get_image_file_path

images_router = APIRouter(
    prefix="/images",
    tags=["images"]
)


@images_router.get("/{image_id}", response_class=FileResponse)
async def get_image(request: Request, image_id: str):
    log.info(f"{request.url}, {request.base_url}")
    image_file_path = get_image_file_path(image_id=image_id)
    return FileResponse(image_file_path)
