from datetime import datetime, timezone

from db import db
from models.Anime import AnimeModel
from models.UserAnimes import user_animes
from sqlalchemy.exc import IntegrityError


class UserModel(db.Model):
    __tablename__ = "users"

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), default="Awesome User")
    role = db.Column(db.String(30), default="user")
    username = db.Column(db.String(70), nullable=False, unique=True)
    email = db.Column(db.String(70), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    activated = db.Column(db.Boolean, default=False)
    joined = db.Column(db.DateTime(), default=datetime.now(timezone.utc))
    saved_animes = db.relationship(
        AnimeModel,
        secondary=user_animes,
        backref=db.backref('users'),
        lazy='dynamic',
    )

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, user_id: str) -> "UserModel":
        return cls.\
            query.\
            filter_by(_id=user_id).\
            with_entities(cls._id, cls.name, cls.role, cls.username, cls.email, cls.activated, cls.joined).\
            first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    def save_anime(self, anime_id: str) -> bool:
        '''Saves an anime to user's collection.'''
        try:
            anime = AnimeModel.find_by_id(anime_id)
            if anime:
                self.saved_animes.append(anime)
                db.session.add(self)
                db.session.commit()
                return True
            return False
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return False

    def remove_anime(self, anime_id: str) -> bool:
        '''Removes an anime from user's collection.'''
        try:
            anime = AnimeModel.find_by_id(anime_id)
            if anime:
                self.saved_animes.remove(anime)
                db.session.add(self)
                db.session.commit()
                return True
            return False
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return False

    def has_user_saved_anime(self, anime_id: str) -> None or 'AnimeModel':
        '''Checks if an anime is in user's collection.'''
        try:
            anime = self.saved_animes.filter_by(anime_id=anime_id).first()
            return anime
        except Exception as ex:
            print(ex)
            return None

    def save_to_db(self) -> str or None:
        try:
            db.session.add(self)
            db.session.commit()
            return self._id
        except IntegrityError as error:
            print(f"[Save User]: {error}")
            db.session.rollback()

    def delete_from_db(self) -> 'sqlalchemy.exc.IntegrityError' or None:
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as error:
            print(f"[Delete User]: {error}")
            db.session.rollback()
            return error
