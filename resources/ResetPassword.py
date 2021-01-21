import os

from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from models.User import UserModel
from models.PasswordReset import PasswordResetModel

from helpers.strings import get_text
from helpers.send_in_blue import SendInBlue, SendInBlueError

FRONTEND_DOMAIN_NAME = os.environ.get('FRONTEND_DOMAIN_NAME', None)


class RequestPasswordReset(Resource):
    '''
    When user requests this endpoint, an email will be sent to the user
    whose account is confirmed along with the link to reset the password.
    '''
    @classmethod
    def post(cls):
        json_data = request.get_json()
        email = json_data.get('email', None)

        if email is None:
            return {
                "message": get_text('reset_password_email_not_present')
            }, 400

        try:
            user = UserModel.find_by_email(email)

            # if there is user with that email,
            # check if the account is confirmed or not
            if user:
                confirmation = user.last_confirmation
                if confirmation:
                    # account not confirmed
                    if not confirmation.confirmed:
                        return {
                            "message": get_text(
                                'reset_password_inactive_account')
                        }, 400

                    # the account is confirmed
                    # check if there is previous token
                    prev_pw_reset = user.password_reset.first()
                    if prev_pw_reset:
                        prev_pw_reset.delete_from_db()

                    # get new password reset hash
                    password_reset = PasswordResetModel(user._id)
                    password_reset.save_to_db()
                    token = password_reset.password_reset_id
                    pw_reset_link = f'{FRONTEND_DOMAIN_NAME}/reset_password?token={token}'

                    # Send email to user
                    SendInBlue.send_pw_reset_email(
                        name=user.name,
                        email=user.email,
                        pw_reset_link=pw_reset_link
                    )
                    return {
                        "message": get_text('reset_password_email_sent'),
                        "token": token
                    }, 200

                # there is no confirmation linked to user's account
                return {
                    "message": get_text('reset_password_inactive_account')
                }, 400

            return {
                "message": get_text('reset_password_user_not_found')
            }, 404

        except SendInBlueError as error:
            print(error)
            return {
                "message": get_text('reset_password_failed_to_send_email')
            }, 500

        except Exception as ex:
            print(ex)
            return {
                "message": get_text('server_error_generic')
            }, 500


class PasswordReset(Resource):
    '''
    Checks if the token is valid. Then proceed with the password reset.
    NEED TO UPDATE THE FLOW!
    Recieve a get request here, checks the token then redirect to password form?
    '''
    @classmethod
    def post(cls):
        try:
            token = request.args.get('token', None)
            new_password = request.get_json().get('new_password', None)

            if token is None:
                return {
                    "message": get_text('reset_password_token_required')
                }, 401

            if new_password is None:
                return {
                    "message": get_text('reset_password_new_password_required')
                }, 400

            reset_password = PasswordResetModel.find_by_id(token)

            if reset_password is None:
                return {
                    "message": get_text('reset_password_token_invalid')
                }, 401

            if reset_password.expired:
                return {
                    "message": get_text('reset_password_token_expired')
                }, 400

            # Token is valid
            user_id = reset_password.user_id
            user = UserModel.find_by_id(user_id)

            if user:
                user.password = generate_password_hash(new_password)
                user.save_to_db()
                # delete the associated password reset row
                reset_password.delete_from_db()

                return {
                    "message": get_text('reset_password_password_updated')
                }, 200

            return {
                "message": get_text('reset_password_user_from_token_not_found')
            }, 404

        except Exception as ex:
            print(ex)
            return {
                "message": get_text('server_error_generic')
            }, 500
