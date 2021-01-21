from uuid import uuid4
from time import time

from db import db

PASSWORD_RESET_EXPIRATION_DELTA = 3600  # 1 hr


class PasswordResetModel(db.Model):
    __tablename__ = 'password_resets'

    password_reset_id = db.Column(db.String(50), primary_key=True)
    expires_at = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.password_reset_id = uuid4().hex
        self.expires_at = int(time()) + PASSWORD_RESET_EXPIRATION_DELTA

    @classmethod
    def find_by_id(cls, _id: str) -> 'PasswordResetModel':
        return cls.query.filter_by(password_reset_id=_id).first()

    @property
    def expired(self) -> bool:
        return int(time()) > self.expires_at

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expires_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
