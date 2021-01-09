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
    get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash
from marshmallow.exceptions import ValidationError

from models.User import UserModel
from schemas.Auth import AuthSchema
from schemas.User import UserSchema

auth_schema = AuthSchema()
user_info_schema = UserSchema()

INORRECT_CREDENTIALS = "Bad credentials."
SERVER_ERROR = "Something went wrong on our servers."
INPUT_ERROR = "Error! please check your input(s)."
USERNAME_EXISTS = "A user with that username already exists. Please use another."
EMAIL_EXISTS = "A user with that email is already registered. Please use another."
INACTIVE_ACCOUNT = "Your account is not active yet. Please check your email to activate your account."
INVALID_CONFIRMATION_TOKEN = "The verification string is either invalid or expired. Please request a new activation email."
REQUEST_NEW_ACTIVATION_EMAIL_URL = "{domain_name}/v1/user/resend_activation_email?email={email}"
ACCOUNT_CONFIRMED = "Thanks for confirming. You may now start to use your account."
EMAIL_NOT_FOUND = "The email you want to confirm does not match our records."
INCOMPLETE_DATA = "Required data are not present."
ACTIVATION_EMAIL_SENT = "An activation email has been sent to your email address."
ACTIVATION_EMAIL_RESENT = "An email will be sent to the address you provided if it was registered before and was not activated."

domain_name = os.environ.get("DOMAIN_NAME")


def generate_activation_token(user) -> str:
    exp_time = datetime.timedelta(hours=5)
    user_claims = {"email": user.email}
    confirmation_token = create_access_token(
        identity=user, expires_delta=exp_time, user_claims=user_claims)

    return confirmation_token


def send_activation_email(**kwargs):
    url = "https://api.sendinblue.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "MyanNime",
            "email": "noreply@myannime.com"
        },
        "to": [
            {
                "email": kwargs["email"],
                "name": kwargs["name"]
            }
        ],
        "params": {
            "NAME": kwargs["name"],
            "ACTIVATION_LINK": kwargs["activation_link"]
        },
        "templateId": 1
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": os.environ.get("SENDINBLUE_API_KEY")
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


class Login(Resource):
    @classmethod
    def post(cls):
        try:
            form_data = auth_schema.load(request.get_json())
            username = form_data.get('username', None)
            password = form_data.get('password', None)

            user = UserModel.find_by_username(username)
            if user and check_password_hash(user.password, password):
                if not user.activated:
                    return {"message": INACTIVE_ACCOUNT}, 403

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
            return {
                'access_token': create_access_token(identity=current_user)
            }, 200

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
            if user_id:
                token = generate_activation_token(new_user)
                activation_link = f"{domain_name}/v1/user/activate?email={new_user.email}&token={token}"
                send_activation_email(
                    name=new_user.name, email=new_user.email, activation_link=activation_link)

                return {"message": ACTIVATION_EMAIL_SENT}, 200

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500


class Activate(Resource):
    @classmethod
    def get(cls):
        token = request.args.get("token", None)
        email = request.args.get("email", None)
        if token and email:
            try:
                decoded = decode_token(token)
                if email and email == decoded.get("user_claims")["email"]:
                    user = UserModel.find_by_email(email)
                    if user and not user.activated:
                        user.activated = True
                        user.save_to_db()
                        print(user.activated)
                        return {"message": ACCOUNT_CONFIRMED}, 200

                return {"message": EMAIL_NOT_FOUND}, 404

            except:
                return {
                    "message": INVALID_CONFIRMATION_TOKEN,
                    "request_email_url": REQUEST_NEW_ACTIVATION_EMAIL_URL.format(domain_name=domain_name, email=email)
                }, 401

        return {"message": INCOMPLETE_DATA}, 400


class ResendActivationEmail(Resource):
    @classmethod
    def get(cls):
        email = request.args.get("email", None)
        if email:
            user = UserModel.find_by_email(email)
            if user and not user.activated:
                token = generate_activation_token(user)
                activation_link = f"{domain_name}/v1/user/activate?email={user.email}&token={token}"
                status_code = send_activation_email(
                    name=user.name, email=user.email, activation_link=activation_link)

                return {"message": ACTIVATION_EMAIL_RESENT}, 200

            return {"message": ACTIVATION_EMAIL_RESENT}, 200

        return {"message": INCOMPLETE_DATA}, 400
