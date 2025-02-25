import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
    UserInfo,
    ChangePassword
)
from resources.Confirmation import Activate, ResendActivationEmail, UserConfirm
from resources.Image import ImageUpload, Image, AvatarGET, AvatarPUT
from resources.ResetPassword import RequestPasswordReset, PasswordReset
from resources.Loader_io import Loader

from helpers.image_helper import IMAGE_SET
from helpers.strings import get_text

app = Flask(__name__)

# .env is loaded automatically when app.run is called
# but our config file is dependent on .env so will have to load manually
load_dotenv('.env', verbose=True)

# load config
app.config.from_object("default_config")
# overrides default config values with config values from APPLICATION_SETTINGS envvar
# i.e., swapping configs is easier
app.config.from_envvar("APPLICATION_SETTINGS")

num_proxies = int(os.environ.get("NUM_PROXIES", 0))

app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=num_proxies)

CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["2/second"],
    headers_enabled=True
)
migrate = Migrate(app, db)
# only call these two lines after setting uploaded_images_dest config.
patch_request_class(app, 10 * 1024 * 1024)  # 10MB upload limit
configure_uploads(app, IMAGE_SET)
#  end
api = Api(app)
jwt = JWTManager(app)


@app.errorhandler(404)
def page_not_found(e):
    PATH = request.path
    response = {
        "message_one": get_text("resource_not_found_1"),
        "message_two": get_text("resource_not_found_2"),
        "requested_path": PATH
    }

    return jsonify(response), 404


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
    print(get_remote_address())
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
api.add_resource(RequestPasswordReset, "/v1/user/send_password_reset_email")
api.add_resource(PasswordReset, "/v1/user/reset_password")
api.add_resource(ChangePassword, "/v1/user/update_password")
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

    if app.config["DEBUG"]:
        @app.before_first_request
        def create_tables():
            # db.drop_all()
            db.create_all()

    app.run(port=5000, debug=True)
