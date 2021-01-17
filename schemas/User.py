from ma import ma
from marshmallow import fields
from models.User import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel


class SaveUserAnimeSchema(ma.Schema):
    class Meta:
        fields = ("anime_id",)


class DumpUserInfoSchema(ma.Schema):
    class Meta:
        fields = (
            "name",
            "username",
            "email",
            "role",
            "joined",
        )
