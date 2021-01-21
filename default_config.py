import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ["DB_URI"]
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.environ["JWT_SECRET"]
UPLOADED_IMAGES_DEST = os.path.join("static", "images")
APP_SECRET = os.environ["APP_SECRET"]
