from ma import ma
# from models.Anime import AnimeModel
from marshmallow import post_dump
from models.Episode import EpisodeModel


class EpisodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EpisodeModel
        include_fk = True
