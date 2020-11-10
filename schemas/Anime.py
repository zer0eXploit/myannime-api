from ma import ma
from models.Anime import AnimeModel
from schemas.Episode import EpisodeSchema


class AnimeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AnimeModel

    genres_list = ma.List(ma.Str())
    genres = ma.Pluck("GenreSchema", "genre_name", many=True)
