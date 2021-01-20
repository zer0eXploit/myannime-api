import os
from time import time

from flask import redirect, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.UserConfirmation import ConfirmationModel
from models.User import UserModel

from schemas.UserConfirm import ConfirmationSchema

from helpers.send_in_blue import SendInBlue, SendInBlueError

confirmation_schema = ConfirmationSchema()

CONFIRMED = "Thanks for confirming. Your account is activated."
ALREADY_CONFIRMED = "This account is already confirmed."
NOT_FOUND = "Invalid token. Please request a new confirmation link."
EXPIRED = "Confirmation link expired. Please request a new one."
USER_NOT_FOUND = "User not found."
RESEND_ACTIVATION_EMAIL_FAILED = "Error resending activation email."
SERVER_ERROR = "Something went wrong on our servers."
RESEND_SUCCESSFUL = "Successfully sent! Please check your email."
TOKEN_REQUIRED = "Activation token is required."
USERNAME_REQUIRED = "Please include username in POST body."
UNAUTHORIZED = "You are not allowed to access this resource. That's all we know."

DOMAIN_NAME = os.environ.get("DOMAIN_NAME")


class Activate(Resource):
    @classmethod
    def get(cls):
        '''Response after successful confirmation or other cases.'''
        if confirmation_id is None:
            return {
                "message": TOKEN_REQUIRED
            }, 400

        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {
                "message": NOT_FOUND
            }, 404

        if confirmation.expired:
            return {
                "message": EXPIRED
            }, 400

        if confirmation.confirmed:
            return {
                "message": ALREADY_CONFIRMED
            }, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        return {
            "message": CONFIRMED
        }, 200


class UserConfirm(Resource):
    @classmethod
    @jwt_required
    def get(cls, username: str):
        '''Get user confirmation. Use for testing.'''
        admin_id = get_jwt_claims().get("admin_id", None)
        print(get_jwt_claims())
        if admin_id is None:
            return {
                "message": UNAUTHORIZED
            }, 403

        user = UserModel.find_by_username(username)

        if not user:
            return {
                "message": USER_NOT_FOUND
            }, 404

        return {
            "username": user.username,
            "current_time": int(time()),
            "confirmations": [
                confirmation_schema.dump(each)
                for each in user.confirmation.order_by(ConfirmationModel.expires_at)
            ],
        }, 200


class ResendActivationEmail(Resource):
    @classmethod
    def post(cls):
        '''Request for a new cofirmatin email.'''
        username = request.get_json().get("username", None)
        if username is None:
            return {
                "message": USERNAME_REQUIRED
            }, 400

        user = UserModel.find_by_username(username)

        if not user:
            return {
                "message": USER_NOT_FOUND
            }, 404

        try:
            confirmation = user.last_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {
                        "message": ALREADY_CONFIRMED
                    }, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user._id)
            new_confirmation.save_to_db()
            token = new_confirmation.confirmation_id
            activation_link = f"{DOMAIN_NAME}/v1/user/activate?token={token}"
            SendInBlue.send_activation_email(
                name=user.name,
                email=user.email,
                activation_link=activation_link
            )

            return {
                "message": RESEND_SUCCESSFUL
            }, 200

        except SendInBlueError as err:
            print(err)
            new_confirmation.delete_from_db()
            return {"message": REGISTERATION_FAILED}, 500

        except Exception as ex:
            print(ex)
            return {
                "message": SERVER_ERROR
            }, 500
