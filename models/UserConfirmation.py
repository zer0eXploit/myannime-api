from uuid import uuid4
from time import time

from db import db

CONFIRMATION_EXPIRATION_DELTA = 3600  # 1 hr


class ConfirmationModel(db.Model):
    __tablename__ = 'confirmations'

    confirmation_id = db.Column(db.String(50), primary_key=True)
    expires_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.confirmation_id = uuid4().hex
        self.expires_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id: str) -> 'ConfirmationModel':
        return cls.query.filter_by(confirmation_id=_id).first()

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
