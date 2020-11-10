from db import db
from sqlalchemy.exc import IntegrityError


class GenreModel(db.Model):
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(50), unique=True, nullable=False)
    genre_explanation = db.Column(
        db.Text, default='Explanation Coming Soon.', nullable=False
    )

    @classmethod
    def get_all_genres(cls) -> 'GenreModel':
        return cls.query.with_entities(cls.genre_name, cls.genre_explanation).order_by(cls.genre_name).all()

    @classmethod
    def find_by_name(cls, genre_name: str) -> "GenreModel":
        return cls.query.filter_by(genre_name=genre_name).first()

    def save_to_db(self) -> str or None:
        try:
            db.session.add(self)
            db.session.commit()
            return self.genre_id
        except IntegrityError as error:
            print(f"[Save Genre]: {error}")
            db.session.rollback()

    def delete_from_db(self) -> 'sqlalchemy.exc.IntegrityError' or None:
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as error:
            print(f"[Delete Genre]: {error}")
            db.session.rollback()
            return error
