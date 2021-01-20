import datetime
import os
import requests

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required
)
from werkzeug.security import check_password_hash, generate_password_hash
from marshmallow.exceptions import ValidationError

from models.User import UserModel
from models.UserConfirmation import ConfirmationModel

from schemas.Auth import AuthSchema
from schemas.User import UserSchema, SaveUserAnimeSchema, DumpUserInfoSchema

from helpers.send_in_blue import SendInBlue, SendInBlueError

auth_schema = AuthSchema()
user_info_schema = UserSchema()
user_anime_save_schema = SaveUserAnimeSchema()
user_min_info_schema = DumpUserInfoSchema()

INORRECT_CREDENTIALS = "Bad credentials."
SERVER_ERROR = "Something went wrong on our servers."
INPUT_ERROR = "Error! please check your input(s)."
USERNAME_EXISTS = "A user with that username already exists. Please use another."
EMAIL_EXISTS = "A user with that email is already registered. Please use another."
INACTIVE_ACCOUNT = "Your account is not active yet. Please check your email to activate your account."
INACTIVE_ACCOUNT_MSG_2 = "If you didn't get an activation email, please request a new one."
INCOMPLETE_DATA = "Required data are not present."
ACTIVATION_EMAIL_SENT = "An activation email has been sent to your email address."
ANIME_SAVED = "Anime saved to user's collection."
USER_NOT_FOUND = "User not found."
SAVE_ANIME_FAILED = "Error saving anime."
ANIME_REMOVED = "Successfully removed anime."
REMOVE_ANIME_FAILED = "Error removing anime."
ANIME_NOT_SAVED_BEFORE = "The anime is not saved to begin with."
ANIME_SAVED_BEFORE = "This anime is already saved."
REGISTERATION_FAILED = "Error registering a new user. Please try again."

DOMAIN_NAME = os.environ.get("DOMAIN_NAME")


class Login(Resource):
    @classmethod
    def post(cls):
        try:
            form_data = auth_schema.load(request.get_json())
            username = form_data.get('username', None)
            password = form_data.get('password', None)

            user = UserModel.find_by_username(username)
            if user and check_password_hash(user.password, password):
                if user.last_confirmation is None:
                    return {
                        "message_1": INACTIVE_ACCOUNT,
                        "message_2": INACTIVE_ACCOUNT_MSG_2
                    }, 403

                activated = user.last_confirmation.confirmed
                if not activated or user.last_confirmation is None:
                    return {
                        "message_1": INACTIVE_ACCOUNT,
                        "message_2": INACTIVE_ACCOUNT_MSG_2
                    }, 403

                exp_time = datetime.timedelta(hours=3)
                access_token = create_access_token(
                    identity=user, expires_delta=exp_time
                )
                refresh_token = create_refresh_token(identity=user)

                return {
                    "name": user.name,
                    "username": user.username,
                    "expires_in": exp_time.total_seconds(),
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200

            return {"message": INORRECT_CREDENTIALS}, 400

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500


class RefreshToken(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        try:
            current_user = get_jwt_identity()
            user = UserModel.find_by_username(current_user)
            if user:
                return {
                    'access_token': create_access_token(identity=user)
                }, 200

            return {
                'message': USER_NOT_FOUND
            }, 404

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500


class Register(Resource):
    @classmethod
    def post(cls):
        try:
            user_info = user_info_schema.load(request.get_json())
            if UserModel.find_by_username(user_info.get("username", None)):
                return {"message": USERNAME_EXISTS}, 409

            if UserModel.find_by_email(user_info.get("email", None)):
                return {"message": EMAIL_EXISTS}, 409

            hashed_password = generate_password_hash(user_info["password"])
            user_info["password"] = hashed_password

            new_user = UserModel(**user_info)
            user_id = new_user.save_to_db()
            confirmation = ConfirmationModel(user_id)
            confirmation.save_to_db()
            if user_id:
                token = confirmation.confirmation_id
                activation_link = f"{DOMAIN_NAME}/v1/user/activate?token={token}"
                try:
                    SendInBlue.send_activation_email(
                        name=new_user.name,
                        email=new_user.email,
                        activation_link=activation_link
                    )

                    return {"message": ACTIVATION_EMAIL_SENT}, 200
                except SendInBlueError as err:
                    print(err)
                    new_user.delete_from_db()
                    confirmation.delete_from_db()
                    return {"message": REGISTERATION_FAILED}, 500

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            confirmation.delete_from_db()
            new_user.delete_from_db()
            return {"message": SERVER_ERROR}, 500


class UserInfo(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        username = get_jwt_identity()
        try:
            user = UserModel.find_by_username(username)
            if user:
                saved_animes = user.saved_animes.\
                    with_entities("anime_info.anime_id", "anime_info.title", "anime_info.poster_uri").\
                    order_by("title").all()
                return {
                    **user_min_info_schema.dump(user),
                    "saved_animes": [
                        {
                            "title": saved_anime[1],
                            "anime_id": str(saved_anime[0]),
                            "poster_uri": saved_anime[2]
                        } for saved_anime in saved_animes
                    ]
                }, 200

            return {
                "message": USER_NOT_FOUND
            }, 404

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500


class SaveAnime(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        try:
            user_id = get_jwt_identity()
            post_data = user_anime_save_schema.load(request.get_json())
            user = UserModel.find_by_username(user_id)
            anime_id = post_data['anime_id']
            if user:
                if user.has_user_saved_anime(anime_id):
                    return {
                        "message": ANIME_SAVED_BEFORE
                    }, 400

                successful = user.save_anime(anime_id)
                if successful:
                    return {
                        "message": ANIME_SAVED
                    }, 201

                return {
                    "message": SAVE_ANIME_FAILED
                }, 400

            return {
                "message": USER_NOT_FOUND
            }, 404

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500

    @classmethod
    @jwt_required
    def delete(cls):
        try:
            user_id = get_jwt_identity()
            data = user_anime_save_schema.load(request.get_json())
            user = UserModel.find_by_username(user_id)
            anime_id = data['anime_id']
            if user:
                if user.has_user_saved_anime(anime_id):
                    successful = user.remove_anime(anime_id)
                    if successful:
                        return {
                            "message": ANIME_REMOVED
                        }, 200

                    return {
                        "message": REMOVE_ANIME_FAILED
                    }, 400

                return {
                    "message": ANIME_NOT_SAVED_BEFORE
                }, 404

            return {
                "message": USER_NOT_FOUND
            }, 404

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500
