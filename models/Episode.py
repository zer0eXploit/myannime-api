from db import db
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import UUID


class EpisodeModel(db.Model):
    __tablename__ = "episodes"

    episode_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    episode_number = db.Column(db.Integer, nullable=False)
    episode_uri_1 = db.Column(db.String(100), nullable=False)
    episode_uri_2 = db.Column(db.String(100), nullable=True)
    episode_uri_3 = db.Column(db.String(100), nullable=True)
    episode_uri_4 = db.Column(db.String(100), nullable=True)
    anime_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("anime_info.anime_id"),
        nullable=False
    )

    @classmethod
    def find_by_id(cls, episode_id) -> "EpisodeModel":
        return cls.query.filter_by(episode_id=episode_id).first()

    def save_to_db(self) -> str or None:
        try:
            db.session.add(self)
            db.session.commit()
            return self.episode_id
        except IntegrityError as error:
            print(f"[Save Episode]: {error}")
            db.session.rollback()

    def delete_from_db(self) -> None or 'sqlalchemy.exc.IntegrityError':
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as error:
            print(f"[Delete Episode]: {error}")
            db.session.rollback()
            return error
