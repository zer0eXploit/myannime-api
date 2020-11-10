from typing import List
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError

from db import db
from models.Genre import GenreModel
from models.AnimeGenres import anime_genres


class AnimeModel(db.Model):
    __tablename__ = "anime_info"

    anime_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    title = db.Column(db.String(80), nullable=False, unique=True)
    rating = db.Column(db.Float, nullable=False)
    release = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(15))
    synopsis = db.Column(db.Text, nullable=False)
    number_of_episodes = db.Column(db.Integer, nullable=False)
    poster_uri = db.Column(db.String(100), nullable=False)
    episodes = db.relationship("EpisodeModel", lazy="dynamic")
    genres = db.relationship(
        GenreModel,
        secondary=anime_genres,
        backref=db.backref('animes', lazy='dynamic'),
        lazy='dynamic',
    )

    @classmethod
    def find_by_name(cls, name: str) -> "AnimeModel":
        return cls.query.filter_by(title=name).first()

    @classmethod
    def find_by_id(cls, anime_id: str) -> "AnimeModel":
        return cls.query.filter_by(anime_id=anime_id).first()

    @classmethod
    def animes_list(cls, page_number: int = 1, sort_method: str = "title") -> List["AnimeModel"]:
        return cls.\
            query.\
            with_entities(cls.anime_id, cls.title, cls.poster_uri, cls.rating).\
            order_by(sort_method).\
            paginate(page_number, 24, False)

    @classmethod
    def find_all(cls) -> List["AnimeModel"]:
        return cls.query.all()

    def save_to_db(self, new_genres_list: List = []) -> str or None:
        try:
            existing_genres = [genre.genre_name for genre in self.genres.all()]
            # checks if existing genres exist in new genre list
            for genre in new_genres_list:
                if not genre in existing_genres:
                    g = GenreModel.find_by_name(genre)
                    if g:
                        self.genres.append(g)

            # checks if existing genres are no longer there in new list
            for old_genre in existing_genres:
                if not old_genre in new_genres_list:
                    g = GenreModel.find_by_name(old_genre)
                    if g:
                        self.genres.remove(g)

            db.session.add(self)
            db.session.commit()
            return self.anime_id
        except IntegrityError as error:
            print(f"[Save Anime]: {error}")
            db.session.rollback()

    def delete_from_db(self) -> 'sqlalchemy.exc.IntegrityError' or None:
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as error:
            print(f"[Delete Anime]: {error}")
            db.session.rollback()
            return error
