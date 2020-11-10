from datetime import datetime, timezone

from db import db

from sqlalchemy.exc import IntegrityError


class AdminModel(db.Model):
    __tablename__ = "admins"

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), default="Awesome Admin")
    role = db.Column(db.String(30), nullable=False, default="Devil")
    username = db.Column(db.String(70), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    joined = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    @classmethod
    def find_by_username(cls, username: str) -> "AdminModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, admin_id: str) -> "AdminModel":
        return cls.\
            query.\
            filter_by(_id=admin_id).\
            with_entities(cls._id, cls.name, cls.role, cls.username, cls.joined).\
            first()

    def save_to_db(self) -> str or None:
        try:
            db.session.add(self)
            db.session.commit()
            return self._id
        except IntegrityError as error:
            print(f"[Save Admin]: {error}")
            db.session.rollback()

    def delete_from_db(self) -> 'sqlalchemy.exc.IntegrityError' or None:
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as error:
            print(f"[Delete Admin]: {error}")
            db.session.rollback()
            return error
