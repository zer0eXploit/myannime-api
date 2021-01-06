import os
import traceback
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims, jwt_optional
from marshmallow import ValidationError

from helpers import image_helper
from schemas.Image import ImageSchema

image_schema = ImageSchema()

INPUT_ERROR = "Error! please check your input(s)."
IMAGE_UPLOADED = "Image {basename} uploaded."
ILLEGAL_UPLOAD = "Illegal file type '{extension}' uploaded."
SERVER_ERROR = "Something went wrong on our servers."
ILLEGAL_FILENAME = "Illegal filename requested."
NOT_FOUND = "File not found."
IMAGE_DELETE_FAILED = "Failed to delete image."
IMAGE_DELETED = "Image deleted."
UNAUTHORIZED = "Unauthorized."
AVATAR_UPLOADED = "Avatar uploaded."


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
                "message": UNAUTHORIZED
            }, 401

        try:
            # request.files = {"form_fild_name" : 'FileStorage' from werkzeug}
            data = image_schema.load(request.files)
            user_id = get_jwt_identity()
            folder = f'user_{user_id}'  # static/images/user_idxxx
            image_path = image_helper.save_image(data['image'], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {
                "message": IMAGE_UPLOADED.format(basename=basename)
            }, 201

        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'])
            return {
                "message": ILLEGAL_UPLOAD.format(extension=extension)
            }, 400

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except:
            return {
                "message": SERVER_ERROR
            }, 500


class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str = None):
        '''
        Looks for the requested image inside user's folder.
        '''
        if not authorized():
            return {
                "message": UNAUTHORIZED
            }, 401

        user_id = get_jwt_identity()
        folder = f'user_{user_id}'
        if not image_helper.is_filename_safe(filename):
            return {
                "message": ILLEGAL_FILENAME
            }, 400

        try:
            return send_file(image_helper.get_path(filename, folder))

        except FileNotFoundError:
            return {
                "message": NOT_FOUND
            }, 404

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        if not authorized():
            return {
                "message": UNAUTHORIZED
            }, 401

        user_id = get_jwt_identity()
        folder = f'user_{user_id}'
        if not image_helper.is_filename_safe(filename):
            return {
                "message": ILLEGAL_FILENAME
            }, 400

        try:
            os.remove(image_helper.get_path(filename, folder))
            return {
                "message": IMAGE_DELETED
            }, 200

        except FileNotFoundError:
            return {
                "message": NOT_FOUND
            }, 404

        except Exception as ex:
            print(ex)
            return {"message": IMAGE_DELETE_FAILED}, 500


class AvatarGET(Resource):
    @classmethod
    @jwt_optional
    def get(cls, username: str):
        try:
            filename = f'user_{username}'
            folder = 'avatars' if not authorized() else 'admin_avatars'
            avatar_path = image_helper.find_image_any_format(filename, folder)
            if avatar_path:
                try:
                    return send_file(avatar_path)

                except FileNotFoundError:
                    return {
                        "message": NOT_FOUND
                    }, 404

            return {
                "message": NOT_FOUND
            }, 404

        except:
            return {
                "message": SERVER_ERROR
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
                    return {"message": IMAGE_DELETE_FAILED}, 500

            try:
                ext = image_helper.get_extension(data['image'].filename)
                avatar = filename + ext
                image_helper.save_image(data["image"], folder, avatar)
                return {
                    "message": AVATAR_UPLOADED
                }, 201

            except UploadNotAllowed:
                extension = image_helper.get_extension(data['image'])
                return {
                    "message": ILLEGAL_UPLOAD.format(extension=extension)
                }, 400

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except:
            return {
                "message": SERVER_ERROR
            }, 500
