from typing import Dict
from flask_restful import Resource
from flask import request

from models.Anime import AnimeModel
from models.Episode import EpisodeModel
from schemas.Anime import AnimeSchema

from helpers.strings import get_text

anime_schema = AnimeSchema()
animes_list_schema = AnimeSchema(many=True)


class AnimesList(Resource):
    @classmethod
    def get(cls) -> Dict:
        try:
            page_number = request.args.get("page", 1, type=int)
            sort_by = request.args.get("sort_by", "title", type=str)

            if sort_by == "rating":
                sort_method = AnimeModel.rating.desc()
            else:
                sort_method = AnimeModel.title

            anime = AnimeModel.animes_list(page_number, sort_method)
            anime_list = {
                "animes": animes_list_schema.dump(anime.items),
                "prev_page": anime.prev_num,
                "next_page": anime.next_num,
                "current_page": anime.page,
                "total_pages": anime.pages
            }

            return anime_list, 200

        except Exception as ex:
            print(ex)

            return {"message": get_text('server_error_generic')}, 500
