from typing import Dict
from flask_restful import Resource
from flask import request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.Anime import AnimeModel

from helpers.check_uuid import valid_uuid4

from schemas.Anime import AnimeSchema
from schemas.Episode import EpisodeSchema

anime_info_schema = AnimeSchema()
episode_schema = EpisodeSchema(many=True)

UUID_ERROR = "Incorrect anime_id format."
ANIME_CREATED = "Anime has been created."
ANIME_UPDATED = "Anime has been updated."
ANIME_DELETED = "Anime ID {anime_id} has been deleted."
ANIME_NOT_FOUND = "Anime {anime_id} is not found."
ANIME_EXISTS = "Anime already exists."
ANIME_NAME_EXISTS = "Anime name already exists."
DELETION_ERROR = "Could not delete anime. Delete the episodes first."
SERVER_ERROR = "Something went wrong on our servers."
INPUT_ERROR = "Error! please check your input(s)."
GENRES_LIST_FIELD_REQUIRED = "Genres list is required."
FORBIDDEN = "You don't have access to the requested resource. That's all we know."


class GetAnime(Resource):
    @classmethod
    def get(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": UUID_ERROR}
            return response, 400

        anime = AnimeModel.find_by_id(anime_id)
        if anime:
            episodes = anime.\
                episodes.\
                with_entities("episode_id", "episode_number").\
                order_by("episode_number").all()

            anime_data = {
                **anime_info_schema.dump(anime),
                "episodes": episode_schema.dump(episodes)
            }
            return anime_data, 200

        return {"message": ANIME_NOT_FOUND.format(anime_id=anime_id)}, 404


class CreateAnime(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        current_user_role = get_jwt_claims().get("role", None)

        print(current_user_role)

        if not current_user_role or current_user_role == "user":
            return {"message": FORBIDDEN}, 403

        try:
            anime_data = anime_info_schema.load(request.get_json())
            genres_list = anime_data.get("genres_list", None)
            if not genres_list:
                return {"message": GENRES_LIST_FIELD_REQUIRED}, 400

            anime_data.pop("genres_list", None)
            anime = AnimeModel(**anime_data)
            anime_id = anime.save_to_db(genres_list)
            if anime_id:
                created_data = {
                    "message": ANIME_CREATED,
                    "anime_id": f"{anime_id}"
                }
                return created_data, 201

            return {"message": ANIME_EXISTS}, 409

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400


class EditAnime(Resource):
    @classmethod
    @jwt_required
    def put(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": UUID_ERROR}
            return response, 400

        try:
            anime_data = anime_info_schema.load(request.get_json())
            genres_list = anime_data.get("genres_list", None)
            if not genres_list:
                return {"message": GENRES_LIST_FIELD_REQUIRED}, 400

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
                    return {"message": ANIME_UPDATED}, 200

                # returns an error from model because anime title naming conflict
                return {"message": ANIME_NAME_EXISTS}, 409

            # if there is no anime with the given id create new one
            anime = AnimeModel(**anime_data)
            anime_id = anime.save_to_db(genres_list)
            if anime_id:
                return {"message": ANIME_CREATED, "anime_id": anime_id}, 200

            # returns an error from model because anime title naming conflict
            return {"message": ANIME_NAME_EXISTS}, 409

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

    @classmethod
    @jwt_required
    def delete(cls, anime_id):
        if not valid_uuid4(anime_id):
            response = {"message": UUID_ERROR}
            return response, 400

        anime = AnimeModel.find_by_id(anime_id)
        if anime:
            info = anime.delete_from_db()
            if not info:
                return {"message": ANIME_DELETED.format(anime_id=anime_id)}, 200

            return {"message": DELETION_ERROR}, 400

        return {"message": ANIME_NOT_FOUND.format(anime_id=anime_id)}, 404
