from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from logging_config import log
from utils.image_management import get_image_file_path

images_router = APIRouter(
    prefix="/images",
    tags=["images"]
)

# In React Native (the frontend) {base_url}/{image_id} won't work
# because it expects the extension of the image file to be appended at the
# end of the url, i.e. {base_url}/{image_id}/some_string.jpg.
# Therefore, the {image_extension} path parameter is used, it doesn't have any significance
# in the functioning of this API.
@images_router.get("/{image_id}/{image_extension}", response_class=FileResponse)
async def get_image(request: Request, image_id: str, image_extension: str):
    log.info(f"{request.url}, {request.base_url}")
    image_file_path = get_image_file_path(image_id=image_id)
    return FileResponse(image_file_path)
