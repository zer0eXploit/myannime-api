import os
from time import time

from flask import redirect, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.UserConfirmation import ConfirmationModel
from models.User import UserModel

from schemas.UserConfirm import ConfirmationSchema

from helpers.send_in_blue import SendInBlue, SendInBlueError
from helpers.strings import get_text

confirmation_schema = ConfirmationSchema()

DOMAIN_NAME = os.environ.get("DOMAIN_NAME")


class Activate(Resource):
    @classmethod
    def get(cls):
        '''Response after successful confirmation or other cases.'''
        confirmation_id = request.args.get("token", None)

        if confirmation_id is None:
            return {
                "message": get_text('confirmation_activation_token_required')
            }, 400

        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {
                "message": get_text('confirmation_token_not_found')
            }, 404

        if confirmation.expired:
            return {
                "message": get_text('confirmation_token_expired')
            }, 400

        if confirmation.confirmed:
            return {
                "message": get_text('confirmation_account_already_confirmed')
            }, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        return {
            "message": get_text('confirmation_account_confirmed')
        }, 200


class UserConfirm(Resource):
    @classmethod
    @jwt_required
    def get(cls, username: str):
        '''Get user confirmation. Use for testing.'''
        admin_id = get_jwt_claims().get("admin_id", None)

        if admin_id is None:
            return {
                "message": get_text('confirmation_unauthorized')
            }, 403

        user = UserModel.find_by_username(username)

        if not user:
            return {
                "message": get_text('confirmation_user_not_found')
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
                "message": get_text('confirmation_username_required')
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
                        "message": get_text('confirmation_account_already_confirmed')
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
                "message": get_text('confirmation_resend_activation_email_success')
            }, 200

        except SendInBlueError as err:
            print(err)
            new_confirmation.delete_from_db()
            return {"message": get_text('confirmation_resend_activation_email_failed')}, 500

        except Exception as ex:
            print(ex)
            return {
                "message": get_text('server_error_generic')
            }, 500
