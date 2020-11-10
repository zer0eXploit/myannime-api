from typing import Dict
from flask_restful import Resource
from flask import request
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import jwt_required

from models.Episode import EpisodeModel

from helpers.check_uuid import valid_uuid4

from schemas.Episode import EpisodeSchema

episode_info_schema = EpisodeSchema()

UUID_ERROR = "Incorrect episode_id format."
EPISODE_CREATED = "Episode has been created."
EPISODE_UPDATED = "Episode has been updated."
ANIME_NOT_FOUND = "Anime with the given ID {anime_id} is not found for the episode."
EPISODE_DELETED = "Episode ID {episode_id} has been deleted."
EPISODE_NOT_FOUND = "Episode ID {episode_id} is not found."
DELETION_ERROR = "Error deletion. Please view the logs if you are a developer."
SERVER_ERROR = "Something went wrong on our servers."
INPUT_ERROR = "Error! please check your input(s)."


class GetEpisode(Resource):
    @classmethod
    def get(cls, episode_id):
        if not valid_uuid4(episode_id):
            response = {"message": UUID_ERROR}
            return response, 400

        episode = EpisodeModel.find_by_id(episode_id)
        if episode:
            episode_data = episode_info_schema.dump(episode)
            return episode_data, 200

        return {"message": EPISODE_NOT_FOUND.format(episode_id=episode_id)}, 404


class CreateEpisode(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        try:
            episode_data = episode_info_schema.load(request.get_json())
            episode = EpisodeModel(**episode_data)
            episode_id = episode.save_to_db()
            if episode_id:
                created_data = {
                    "message": EPISODE_CREATED,
                    "episode_id": f"{episode_id}"
                }
                return created_data, 201

            return {"message": ANIME_NOT_FOUND.format(anime_id=episode_data["anime_id"])}, 404

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400


class EditEpisode(Resource):
    @classmethod
    @jwt_required
    def put(cls, episode_id):
        if not valid_uuid4(episode_id):
            response = {"message": UUID_ERROR}
            return response, 400

        try:
            episode = EpisodeModel.find_by_id(episode_id)
            if episode:
                episode_info = episode_info_schema.load(request.get_json())
                episode.episode_number = episode_info["episode_number"]
                episode.episode_uri_1 = episode_info.get("episode_uri_1")
                episode.episode_uri_2 = episode_info.get("episode_uri_2")
                episode.episode_uri_3 = episode_info.get("episode_uri_3")
                episode.episode_uri_4 = episode_info.get("episode_uri_4")
                episode.next_episode = episode_info.get("next_episode")
                episode.prev_episode = episode_info.get("prev_episode")
                episode.anime_id = episode_info.get("anime_id")
                episode_id = episode.save_to_db()
                if episode_id:
                    return {"message": EPISODE_UPDATED}, 200

                return {"message": ANIME_NOT_FOUND.format(anime_id=episode_info["anime_id"])}, 404

            return {"message": EPISODE_NOT_FOUND.format(episode_id=episode_id)}, 404

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

    @classmethod
    @jwt_required
    def delete(cls, episode_id):
        if not valid_uuid4(episode_id):
            response = {
                "message": UUID_ERROR
            }
            return response, 400

        try:
            episode_to_delete = EpisodeModel.find_by_id(episode_id)
            if episode_to_delete:
                info = episode_to_delete.delete_from_db()
                if not info:
                    response_message = {
                        "message": EPISODE_DELETED.format(episode_id=episode_id)
                    }
                    return response_message, 200

                return {"message": DELETION_ERROR}, 400

            response_message = {
                "message": EPISODE_NOT_FOUND.format(episode_id=episode_id)
            }
            return response_message, 404

        except Exception as ex:
            print(f"[Delete Episode]: {ex}")
            response_message = {
                "message": SERVER_ERROR
            }
            return response_message, 500
