import hashlib
import os
import shutil
from typing import List

from fastapi import UploadFile

from logging_config import log
from utils.date_time import get_current_utc_datetime

BASE_PATH = os.path.join(os.getcwd(), "images")


def write_images(truck_id: str, files: List[UploadFile]):
    """writes a list of uploaded images to filesystem and returns the path
    where the images are stored

    Args:
        truck_id (str)
        files (List[UploadFile])
    """

    file_paths = []
    for file in files:
        file_path = write_image(truck_id=truck_id, file=file)
        if file_path:
            file_paths.append(file_path)
        else:
            delete_path(truck_id=truck_id)
            file_paths = []
            break

    return file_paths


def write_image(truck_id: str, file: UploadFile):
    """given a truck_id and file like objects writes the file
    to path images/{truck_id}/dt_filenamehash.extension

    Args:
        truck_id (str)
        file (UploadFile)

    Returns:
        _type_: _description_
    """
    directory_path = f"{BASE_PATH}/{truck_id}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    filename = get_filename(filename=file.filename)
    file_path = f"{directory_path}/{filename}"

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        log.error(f"error copying {file.filename} for truck_id {truck_id} : {str(e)}")
        return False

    return file_path


def get_filename(filename: str) -> str:
    """returns a hash of filename with current utc time"""
    filename, extension = os.path.splitext(filename)
    hash = hashlib.md5(string=f"{get_current_utc_datetime()}_{filename}".encode())
    return f"{hash.hexdigest()}{extension}"


def delete_path(truck_id: str):
    """deletes the images/{truck_id} dir in case write fails

    Args:
        truck_id (str)
    """
    return shutil.rmtree(path=f"{BASE_PATH}/{truck_id}")
