from fastapi import APIRouter, UploadFile, Request
from utils.image_management import save_image, generate_image_url, delete_image
from data.db import get_upload_images_demo_collection

upload_images_demo_router = APIRouter(
    prefix="/upload-images-demo",
    tags=["upload-images-demo"]
)

# putting the database code in the same file only for demonstration purposes
# data related code should always be in the data package
upload_images_demo_collection = get_upload_images_demo_collection()


@upload_images_demo_router.post("/upload-image-demo")
async def upload_image_demo(image: UploadFile):
    # the save_image() util function is an async function, it should always be called
    # from an async function with the await keyword
    image_id = await save_image(image_file=image)

    # saving the image id in the database for later usages
    # caution: this is for demonstration purposes, database code should always be in data package
    upload_images_demo_collection.insert_one({"image_id": image_id})

    return {"status": "OK"}


@upload_images_demo_router.get("/get-all-image-urls")
async def get_all_image_url(request: Request):
    uploaded_images = upload_images_demo_collection.find()

    uploaded_image_ids = [image["image_id"] for image in uploaded_images]

    generated_url_list = [generate_image_url(image_id=image_id, request=request)
                          for image_id in uploaded_image_ids]

    return {"image_url_list": generated_url_list}


@upload_images_demo_router.delete("/delete-all-uploaded-images-demo")
async def delete_all_uploaded_images_demo():
    uploaded_images = upload_images_demo_collection.find()

    uploaded_image_ids = [image["image_id"] for image in uploaded_images]

    result = False

    # deleting from the database collection
    for image_id in uploaded_image_ids:
        upload_images_demo_collection.delete_one({"image_id": image_id})

    # deleting from the file_system with the help of the delete_image util function
    for image_id in uploaded_image_ids:
        # delete_image util function is an async function, and it should always be awaited
        result = await delete_image(image_id=image_id)

    return {"status": result}
