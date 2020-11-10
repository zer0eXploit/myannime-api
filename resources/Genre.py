from flask_restful import Resource
from models.Genre import GenreModel
from models.Anime import AnimeModel
from schemas.Genre import GenreSchema
from schemas.Anime import AnimeSchema
from marshmallow.exceptions import ValidationError
from flask import request
from flask_jwt_extended import jwt_required

genre_information_schema = GenreSchema()
animes_list_schema = AnimeSchema(many=True)
genres_list_schema = GenreSchema(many=True)

GENRE_CREATED = "Genre has been created."
GENRE_CREATION_ERROR = "Genre could not be created. Please try again."
GENRE_UPDATED = "Genre has been updated."
GENRE_EXISTS = "The genre already exists."
GENRE_DELETED = "Genre deleted."
GENRE_NOT_FOUND = "Specified genre is not found. If it is a valid genre, please pm us. :)"
GENRE_NOT_FOUND_DELETION = "Genre is not found. Please double check."
SERVER_ERROR = "Something went wrong on our servers. If you === dev, check logs."
INPUT_ERROR = "Error! please check your input(s)."


class GenreInfo(Resource):
    @classmethod
    def get(cls, genre_name):
        try:
            # replaces '-' with spaces, and makes the first letter capital.
            genre_name = " ".join(genre_name.split("-")).capitalize()
            page_number = request.args.get("page", 1, type=int)
            sort_by = request.args.get("sort_by", "title", type=str)

            if sort_by == "rating":
                sort_method = AnimeModel.rating.desc()
            else:
                sort_method = AnimeModel.title

            genre = GenreModel.find_by_name(genre_name=genre_name)
            if genre:
                anime = genre.\
                    animes.\
                    with_entities(AnimeModel.anime_id, AnimeModel.title,
                                  AnimeModel.poster_uri, AnimeModel.rating).\
                    order_by(sort_method).\
                    paginate(page_number, 24, False)

                response_data = {
                    **genre_information_schema.dump(genre),
                    "animes": animes_list_schema.dump(anime.items),
                    "prev_page": anime.prev_num,
                    "next_page": anime.next_num,
                    "current_page": anime.page,
                    "total_pages": anime.pages,
                    "sorted_by": sort_by
                }

                return response_data, 200

            return {"message": GENRE_NOT_FOUND}, 404

        except Exception as error:
            print(error)
            return {"message": SERVER_ERROR}, 500


class Genres(Resource):
    '''
    GET: responds with a list of all genres
    POST: accepts genre_name, genre_explanation and creates it if not exists already.
    PUT: accepts genre_name and genre_explanation to update. creates it if not exists already.
    DELETE: accepts genre_name to be deleted from that genres.
    '''
    @classmethod
    def get(cls):
        genres = GenreModel.get_all_genres()
        response = genres_list_schema.dump(genres)
        return {"genres": response}, 200

    @classmethod
    @jwt_required
    def post(cls):
        try:
            post_data = request.get_json()
            genre_data = genre_information_schema.load(post_data)
            genre_data["genre_name"] = genre_data["genre_name"].capitalize()
            genre = GenreModel.find_by_name(genre_data.get("genre_name", None))
            if not genre:
                try:
                    genre = GenreModel(**genre_data)
                    genre_id = genre.save_to_db()
                    if genre_id:
                        return {"message": GENRE_CREATED}, 201

                    return {"message": GENRE_CREATION_ERROR}, 500

                except Exception as error:
                    print(error)
                    return {"message": SERVER_ERROR}, 500

            return {"message": GENRE_EXISTS}, 409

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

    @classmethod
    @jwt_required
    def put(cls):
        try:
            put_data = request.get_json()
            genre_data = genre_information_schema.load(put_data)
            genre_data["genre_name"] = genre_data["genre_name"].capitalize()
            try:
                genre = GenreModel.find_by_name(genre_data["genre_name"])
                if not genre:
                    genre = GenreModel(**genre_data)
                    genre_id = genre.save_to_db()
                    if genre_id:
                        return {"message": GENRE_CREATED}, 201

                    return {"message": GENRE_CREATION_ERROR}, 500

                genre.genre_explanation = genre_data["genre_explanation"]
                genre.save_to_db()
                return {"message": GENRE_UPDATED}, 200

            except Exception as error:
                print(error)
                return {"message": SERVER_ERROR}, 500

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400

    @classmethod
    @jwt_required
    def delete(cls):
        try:
            post_data = request.get_json()
            genre_info = genre_information_schema.load(post_data)
            genre = GenreModel.find_by_name(genre_info["genre_name"])

            if genre:
                try:
                    genre.delete_from_db()
                    return {"message": GENRE_DELETED}, 200

                except Exception as error:
                    print(error)
                    return {"message": SERVER_ERROR}, 500

            return {"message": GENRE_NOT_FOUND_DELETION}, 404

        except ValidationError as error:
            return {"message": INPUT_ERROR, "info": error.messages}, 400
