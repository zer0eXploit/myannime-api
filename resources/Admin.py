from flask_restful import Resource
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.Admin import AdminModel
from schemas.Admin import AdminSchema

admin_schema = AdminSchema()

ADMIN_REGISTERED = "Admin registeration successful."
USERNAME_EXISTS = "An admin with that username already exists. Please try another."
ADMIN_REGISTERATION_ERROR = "An error occurred while registering your info. Please try again."
ADMIN_NOT_FOUND = "Admin not found."
SERVER_ERROR = "Something went wrong on our servers."
INPUT_ERROR = "Error! please check your input(s)."
ACC_INFO_ACCESS_FORBIDDEN = "God level admin access required to view others' profile."
ACC_CREATION_FORBIDDEN = "God level admin access required to create another admin."
UNAUTHORIZED_TO_DELETE = "Unauthorized to delete."
ADMIN_DELETED = "The admin has been deleted."
ADMIN_UPDATED = "Admin info has been updated."
UNAUTHORIZED_TO_UPDATE = "Unauthorized to modify admin info."

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

            return {"message": ACC_INFO_ACCESS_FORBIDDEN}, 403

        return {"message": ADMIN_NOT_FOUND}


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
                    return {"message": USERNAME_EXISTS}, 409

                hashed_password = generate_password_hash(
                    admin_info["password"])
                admin_info["password"] = hashed_password
                admin = AdminModel(**admin_info)
                admin_id = admin.save_to_db()

                if admin_id:
                    return {"message": ADMIN_REGISTERED, "admin_id": admin_id}, 201

                return {"message": ADMIN_REGISTERATION_ERROR}, 500

            except ValidationError as error:
                return {"message": INPUT_ERROR, "info": error.messages}, 400

            except Exception as ex:
                print(ex)
                return {"message": SERVER_ERROR}, 500

        return {"message": ACC_CREATION_FORBIDDEN}, 403

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
                    return {"message": ADMIN_UPDATED}, 200
                elif condition_two:
                    admin.name = admin_info.get("name")
                    admin.role = admin_info.get("role")
                    return {"message": ADMIN_UPDATED}, 200

                return {"message": UNAUTHORIZED_TO_UPDATE}, 401

            return {"message": ADMIN_NOT_FOUND}

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500

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
                    return {"message": ADMIN_DELETED}, 200

                return {"message": UNAUTHORIZED_TO_DELETE}, 401

            return {"message": ADMIN_NOT_FOUND}

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

        except Exception as ex:
            print(ex)
            return {"message": SERVER_ERROR}, 500
