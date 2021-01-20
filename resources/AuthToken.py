import datetime

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from marshmallow.exceptions import ValidationError

from models.Admin import AdminModel
from schemas.Auth import AuthSchema

from helpers.strings import get_text

auth_schema = AuthSchema()


class RequestToken(Resource):
    @classmethod
    def post(cls):
        try:
            form_data = auth_schema.load(request.get_json())
            username = form_data.get('username', None)
            password = form_data.get('password', None)
            admin = AdminModel.find_by_username(username)
            if admin and check_password_hash(admin.password, password):
                exp_time = datetime.timedelta(hours=1)
                access_token = create_access_token(
                    identity=admin, expires_delta=exp_time
                )
                refresh_token = create_refresh_token(identity=admin)

                return {"access_token": access_token, "refresh_token": refresh_token}, 200

            return {"message": get_text('admin_auth_incorrect_credentials')}, 400

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": get_text('server_error_generic')}, 500
