import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES
from PIL import Image

# set name and allowed extensions
# the image will be saved under static/images/image_name.extension
# app.config["UPLOADED_IMAGES_DEST"] = os.path.join("static", "images")
# IMAGES from "UPLOADED_IMAGES_DEST" and images from UploadSet's first arguent must be the same.
IMAGE_SET = UploadSet('images', IMAGES)


def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    '''
    Takes FileStorage and saves it to a folder.
    '''
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str = None, folder: str = None) -> str:
    '''
    Takes image name and folder and return full path.
    '''
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename: str = None, folder: str = None) -> Union[str, None]:
    '''
    Takes an image name without extension and return image of the any accepted formats.
    '''
    for _format in IMAGES:
        image = f'{filename}.{_format}'
        image_path = get_path(image, folder)
        if os.path.isfile(image_path):
            return image_path
    return None


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    '''Takes a FileStorage and returns filename.'''
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    '''Check our regex and return whether the string matches or not.'''
    filename = _retrieve_filename(file)
    allowed_formats = "|".join(IMAGES)  # jpg|png|jpeg etc.,
    regex = f'^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_formats})$'

    # re.match returns a match data if match is found None otherwise
    return re.match(regex, filename) is not None


def get_basename(file: Union[str, FileStorage]) -> str:
    '''Returns fullname of image in path.
    get_basename('some/folder/image.jpg') -> 'image.jpg'
    '''
    filename = _retrieve_filename(file)
    return os.path.split(filename)[1]


def get_extension(file: Union[str, FileStorage]) -> str:
    '''Returns file extension.'''
    filename = _retrieve_filename(file)
    return os.path.splitext(filename)[1]


def get_name_without_ext(filename: str) -> str:
    '''Strips filename from filename.ext'''
    return os.path.splitext(filename)[0]


def change_image_type_and_resize(image_path: str, filename: str) -> None:
    '''Changes the image type to jpg'''
    image_path = f'{image_path}/{filename}'
    image = Image.open(image_path)
    image.thumbnail((500, 500))
    image.save(image_path)
    return None
