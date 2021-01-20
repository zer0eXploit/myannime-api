import os

from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename

from db import db
from ma import ma
from resources.Root import Root
from resources.Anime import AnimesList
from resources.Anime_CRUD import GetAnime, CreateAnime, EditAnime
from resources.Episode_CRUD import GetEpisode, CreateEpisode, EditEpisode
from resources.Genre import GenreInfo, Genres
from resources.Admin import GetAdmin as Admin, CreateAdmin
from resources.AuthToken import RequestToken
from resources.User import (
    Login,
    Register,
    RefreshToken,
    SaveAnime,
    UserInfo
)
from resources.Confirmation import Activate, ResendActivationEmail, UserConfirm
from resources.Image import ImageUpload, Image, AvatarGET, AvatarPUT
from resources.Loader_io import Loader

from helpers.image_helper import IMAGE_SET
from helpers.strings import get_text

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
app.config["DEBUG"] = True
app.config["UPLOADED_IMAGES_DEST"] = os.path.join("static", "images")
app.secret_key = os.environ.get("APP_SECRET")


@app.errorhandler(404)
def page_not_found(e):
    PATH = request.path
    response = {
        "message_one": get_text("resource_not_found_1"),
        "message_two": get_text("resource_not_found_2"),
        "requested_path": PATH
    }

    return jsonify(response), 404


CORS(app)
migrate = Migrate(app, db)
# only call these two lines after setting uploaded_images_dest config.
patch_request_class(app, 10 * 1024 * 1024)  # 10MB upload limit
configure_uploads(app, IMAGE_SET)
#  end
api = Api(app)
jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    if user and hasattr(user, "role"):
        if user.role != "Regular Member":
            claims = {
                "admin_id": user._id,
                "name": user.name,
                "role": user.role
            }

            return claims


@jwt.user_identity_loader
def user_identity_lookup(user):
    if hasattr(user, 'username'):
        return user.username


@app.route("/favicon.ico")
def get():
    icon_path = os.path.join(app.root_path, "static/images")
    mimetype = "image/vnd.microsoft.icon"
    icon_name = "favicon.ico"

    return send_from_directory(icon_path, icon_name, mimetype=mimetype)


api.add_resource(Root, "/")
api.add_resource(AnimesList, "/v1/animes")
api.add_resource(GetAnime, "/v1/anime/<string:anime_id>")
api.add_resource(CreateAnime, "/v1/create/anime")
api.add_resource(EditAnime, "/v1/edit/anime/<string:anime_id>")
api.add_resource(GetEpisode, "/v1/episode/<string:episode_id>")
api.add_resource(CreateEpisode, "/v1/create/episode")
api.add_resource(EditEpisode, "/v1/edit/episode/<string:episode_id>")
api.add_resource(Genres, "/v1/genres")
api.add_resource(GenreInfo, "/v1/genre/<string:genre_name>")
api.add_resource(Admin, "/v1/operators/admin/<int:admin_id>")
api.add_resource(CreateAdmin, "/v1/operators/admin")
api.add_resource(RequestToken, "/v1/operators/request_token")
api.add_resource(Login, "/v1/user/login")
api.add_resource(RefreshToken, "/v1/user/refresh")
api.add_resource(Register, "/v1/user/register")
api.add_resource(Activate, "/v1/user/activate")
api.add_resource(ResendActivationEmail, "/v1/user/resend_activation_email")
api.add_resource(UserConfirm, "/v1/user/confirm_status/<string:username>")
api.add_resource(ImageUpload, "/v1/upload/image")
api.add_resource(Image, "/v1/image/<string:filename>")
api.add_resource(UserInfo, "/v1/user/info")
api.add_resource(AvatarGET, "/v1/user/avatar/<string:username>")
api.add_resource(AvatarPUT, "/v1/user/avatar")
api.add_resource(SaveAnime, "/v1/user/save_anime")
api.add_resource(Loader, "/loaderio-b8a35b9227646ad0cb661aa0a227f084/")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)

    # if app.config["DEBUG"]:
    # @app.before_first_request
    # def create_tables():
    #     # db.drop_all()
    #     db.create_all()

    app.run(port=5000, debug=True)
