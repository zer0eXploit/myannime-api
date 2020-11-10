from ma import ma
from marshmallow import Schema, fields
from models.Genre import GenreModel


class GenreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GenreModel
        exclude = ("genre_id",)
