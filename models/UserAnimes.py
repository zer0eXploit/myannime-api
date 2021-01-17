from db import db
from sqlalchemy.dialects.postgresql import UUID


user_animes = db.Table(
    "user_animes",
    db.Column(
        "anime_id",
        UUID(as_uuid=True),
        db.ForeignKey("anime_info.anime_id")
    ),
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users._id")
    )
)
