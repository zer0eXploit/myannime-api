import os
import traceback
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims, jwt_optional
from marshmallow import ValidationError

from helpers import image_helper
from helpers.sirv import Sirv
from helpers.strings import get_text

from schemas.Image import ImageSchema

image_schema = ImageSchema()

# Sirv setup
client_id = os.environ.get('SIRV_CLIENT_ID', None)
client_secret = os.environ.get('SIRV_CLIENT_SECRET', None)
sirv_utils = Sirv(client_id, client_secret)
SIRV_BASE_FOLDER_NAME = "MYANNime"


def authorized():
    '''Checks if admin or not.'''
    role = get_jwt_claims().get("role", None)
    return role is not None


class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        '''
        Used to upload an image file.
        Uses JWT to retrieve user info and then saves the image to the user's folder.
        If there is a filename conflict, it appends a number at the end.
        '''
        if not authorized():
            return {
                "message": get_text('image_unauthorized')
            }, 401

        try:
            # request.files = {"form_fild_name" : 'FileStorage' from werkzeug}
            data = image_schema.load(request.files)
            user_id = get_jwt_identity()
            folder = f'admin_{user_id}'  # static/images/user_idxxx
            image_path = image_helper.save_image(data['image'], folder=folder)
            basename = image_helper.get_basename(image_path)
            absolute_path = f'{os.getcwd()}/static/images/{folder}'
            image_url = sirv_utils.upload(
                basename, absolute_path, SIRV_BASE_FOLDER_NAME)

            return {
                "message": get_text('image_photo_uploaded').format(basename=basename),
                "image_url": image_url["image_path"]
            }, 201

        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'])
            return {
                "message": get_text('image_illegal_file_type').format(extension=extension)
            }, 400

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {

            }, 500


class Image(Resource):
    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        if not authorized():
            return {
                "message": get_text('image_unauthorized')
            }, 401

        if not image_helper.is_filename_safe(filename):
            return {
                "message": get_text('image_illegal_file_name')
            }, 400

        user_id = get_jwt_identity()
        user_folder = f'admin_{user_id}'

        try:
            sirv_utils.delete(filename, SIRV_BASE_FOLDER_NAME)
            return {
                "message": get_text('image_deletion_successful')
            }

        except Exception as ex:
            print(ex)
            return {"message": get_text('image_deletion_failed')}, 500


class AvatarGET(Resource):
    @classmethod
    @jwt_optional
    def get(cls, username: str):
        AVATAR_FOLDER = 'avatars' if not authorized() else 'admin_avatars'
        try:
            filename = f'user_{username}'
            avatar_path = image_helper.find_image_any_format(
                filename, AVATAR_FOLDER)
            if avatar_path:
                try:
                    return send_file(avatar_path)

                except FileNotFoundError:
                    return {
                        "message": get_text('image_file_not_found')
                    }, 404

            return {
                "message": get_text('image_file_not_found')
            }, 404

        except:
            return {

            }, 500


class AvatarPUT(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        try:
            data = image_schema.load(request.files)
            filename = f'user_{get_jwt_identity()}'
            folder = 'avatars' if not authorized() else 'admin_avatars'
            avatar_path = image_helper.find_image_any_format(filename, folder)
            if avatar_path:
                try:
                    os.remove(avatar_path)

                except Exception as ex:
                    print(ex)

            try:
                absolute_path = f'{os.getcwd()}/static/images/{folder}'
                ext = image_helper.get_extension(data['image'].filename)
                avatar = filename + ext
                image_helper.save_image(data["image"], folder, avatar)
                image_helper.change_image_type_and_resize(
                    absolute_path, avatar)
                return {
                    "message": get_text('image_avatar_uploaded')
                }, 201

            except UploadNotAllowed:
                extension = image_helper.get_extension(data['image'])
                return {
                    "message": get_text('image_illegal_file_type').format(extension=extension)
                }, 400

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {

            }, 500
