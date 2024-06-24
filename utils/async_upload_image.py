import os

import aiofiles
from config import IMAGES_UPLOAD_FOLDER
from fastapi import UploadFile
from utils.sanitize_filename import secure_filename


async def async_upload_image(image: UploadFile) -> str:
    """
    Uploads an image file to a server or cloud storage and returns the path or URL of the uploaded image.
    """
    # Example implementation for uploading to a local server
    # Ensure to implement error handling, security checks, and validation as per your application's needs.

    # Generate a unique filename or use the original filename with some prefix/suffix
    filename = secure_filename(image.filename)  # You might need to sanitize the filename
    upload_path = os.path.join(IMAGES_UPLOAD_FOLDER, filename)

    # Open the file and write the contents in chunks
    async with aiofiles.open(upload_path, 'wb') as buffer:
        while True:
            chunk = await image.read(1024)  # Read the image file in chunks
            if not chunk:
                break
            await buffer.write(chunk)

    return upload_path  # Return the path where the image was uploaded
