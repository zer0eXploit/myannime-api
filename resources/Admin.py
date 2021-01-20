from flask_restful import Resource
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.Admin import AdminModel
from schemas.Admin import AdminSchema

from helpers.strings import get_text

admin_schema = AdminSchema()

role = None
authenticated_admin_id = None


def get_admin_role_and_id():
    '''
    Extract role and user_id from jwt and set them into constatnts.
    '''
    global role
    global authenticated_admin_id

    role = get_jwt_claims().get("role", None)
    authenticated_admin_id = get_jwt_claims().get("admin_id", None)


class GetAdmin(Resource):
    @classmethod
    @jwt_required
    def get(cls, admin_id):
        get_admin_role_and_id()
        admin = AdminModel.find_by_id(admin_id)
        if admin:
            if authenticated_admin_id == admin._id or role == "God":
                admin_info = admin_schema.dump(admin)

                return admin_info, 200

            return {"message": get_text('admin_acc_info_access_forbidden')}, 403

        return {"message": get_text('admin_not_found')}


class CreateAdmin(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        get_admin_role_and_id()
        if role == "God":
            try:
                admin_info = admin_schema.load(request.get_json())
                admin = AdminModel.find_by_username(admin_info["username"])
                if admin:
                    return {"message": get_text('admin_username_exists')}, 409

                hashed_password = generate_password_hash(
                    admin_info["password"])
                admin_info["password"] = hashed_password
                admin = AdminModel(**admin_info)
                admin_id = admin.save_to_db()

                if admin_id:
                    return {"message": get_text('admin_registered'), "admin_id": admin_id}, 201

                return {"message": get_text('admin_registeration_error')}, 500

            except ValidationError as error:
                return {"message": get_text('input_error_generic'), "info": error.messages}, 400

            except Exception as ex:
                print(ex)
                return {"message": get_text('server_error_generic')}, 500

    @classmethod
    @jwt_required
    def put(cls):
        get_admin_role_and_id()
        try:
            admin_info = admin_schema.load(request.get_json())
            username = admin_info.get("username", None)
            password = admin_info.get("password", None)
            admin = AdminModel.find_by_username(username)

            if admin:
                condition_one = (admin._id == authenticated_admin_id) and\
                    check_password_hash(admin.password, password)
                condition_two = role == "God"

                if condition_one:
                    admin.name = admin_info.get("name")
                    return {"message": get_text('admin_info_updated')}, 200
                elif condition_two:
                    admin.name = admin_info.get("name")
                    admin.role = admin_info.get("role")
                    return {"message": get_text('admin_info_updated')}, 200

                return {"message": get_text('admin_info_modification_forbidden')}, 401

            return {"message": get_text('admin_not_found')}

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": get_text('server_error_generic')}, 500

    @classmethod
    @jwt_required
    def delete(cls):
        get_admin_role_and_id()
        try:
            admin_info = admin_schema.load(request.get_json())
            username = admin_info.get("username", None)
            password = admin_info.get("password", None)
            admin = AdminModel.find_by_username(username)

            if admin:
                condition_one = (admin._id == authenticated_admin_id) and\
                    check_password_hash(admin.password, password)
                condition_two = role == "God"

                if condition_one or condition_two:
                    admin.delete_from_db()
                    return {"message": get_text('admin_deleted')}, 200

                return {"message": get_text('admin_unauthorized_deletion')}, 401

            return {"message": get_text('admin_not_found')}

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": get_text('server_error_generic')}, 500
