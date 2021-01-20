from typing import Dict
from flask_restful import Resource
from flask import request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_optional, get_jwt_identity

from models.Anime import AnimeModel
from models.User import UserModel

from helpers.check_uuid import valid_uuid4
from helpers.strings import get_text

from schemas.Anime import AnimeSchema
from schemas.Episode import EpisodeSchema

anime_info_schema = AnimeSchema()
episode_schema = EpisodeSchema(many=True)


class GetAnime(Resource):
    @classmethod
    @jwt_optional
    def get(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": get_text('anime_uuid_error')}
            return response, 400

        anime = AnimeModel.find_by_id(anime_id)
        username = get_jwt_identity()
        anime_bookmarked = False

        if username:  # if there is an authenticated user
            # get the user and check if he saved the anime
            user = UserModel.find_by_username(username)
            if user.has_user_saved_anime(anime_id):
                anime_bookmarked = True

        if anime:
            episodes = anime.\
                episodes.\
                with_entities("episode_id", "episode_number").\
                order_by("episode_number").all()

            anime_data = {
                **anime_info_schema.dump(anime),
                "anime_bookmarked": anime_bookmarked,
                "episodes": episode_schema.dump(episodes)
            }
            return anime_data, 200

        return {"message": get_text('anime_not_found').format(anime_id=anime_id)}, 404


class CreateAnime(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        current_user_role = get_jwt_claims().get("role", None)

        if not current_user_role or current_user_role == "Regular Member":
            return {"message": get_text('anime_access_forbidden')}, 403

        try:
            anime_data = anime_info_schema.load(request.get_json())
            genres_list = anime_data.get("genres_list", None)
            if not genres_list:
                return {"message": get_text('anime_genres_required')}, 400

            anime_data.pop("genres_list", None)
            anime = AnimeModel(**anime_data)
            anime_id = anime.save_to_db(genres_list)
            if anime_id:
                created_data = {
                    "message": get_text('anime_created'),
                    "anime_id": f"{anime_id}"
                }
                return created_data, 201

            return {"message": get_text('anime_already_exists')}, 409

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400


class EditAnime(Resource):
    @classmethod
    @jwt_required
    def put(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": get_text('anime_uuid_error')}
            return response, 400

        current_user_role = get_jwt_claims().get("role", None)

        if not current_user_role or current_user_role == "Regular Member":
            return {"message": get_text('anime_access_forbidden')}, 403

        try:
            anime_data = anime_info_schema.load(request.get_json())
            genres_list = anime_data.get("genres_list", None)
            if not genres_list:
                return {"message": get_text('anime_genres_required')}, 400

            anime_data.pop("genres_list", None)
            anime = AnimeModel.find_by_id(anime_id)
            if anime:
                anime.title = anime_data["title"]
                anime.rating = anime_data["rating"]
                anime.release = anime_data["release"]
                anime.status = anime_data["status"]
                anime.synopsis = anime_data["synopsis"]
                anime.number_of_episodes = anime_data["number_of_episodes"]
                anime.poster_uri = anime_data["poster_uri"]
                anime_id = anime.save_to_db(genres_list)
                if anime_id:
                    return {"message": get_text('anime_updated')}, 200

                # returns an error from model because anime title naming conflict
                return {"message": get_text('anime_name_exists')}, 409

            # if there is no anime with the given id create new one
            anime = AnimeModel(**anime_data)
            anime_id = anime.save_to_db(genres_list)
            if anime_id:
                return {"message": get_text('anime_created'), "anime_id": anime_id}, 200

            # returns an error from model because anime title naming conflict
            return {"message": get_text('anime_name_exists')}, 409

        except ValidationError as error:
            return {"message": get_text('input_error_generic'), "info": error.messages}, 400

    @classmethod
    @jwt_required
    def delete(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": get_text('anime_uuid_error')}
            return response, 400

        current_user_role = get_jwt_claims().get("role", None)
        if not current_user_role or current_user_role == "Regular Member":
            return {"message": get_text('anime_access_forbidden')}, 403

        anime = AnimeModel.find_by_id(anime_id)
        if anime:
            info = anime.delete_from_db()
            if not info:
                return {"message": get_text('anime_deleted').format(anime_id=anime_id)}, 200

            return {"message": get_text('anime_deletion_error')}, 400

        return {"message": get_text('anime_not_found').format(anime_id=anime_id)}, 404
