from db import db
from sqlalchemy.dialects.postgresql import UUID


anime_genres = db.Table(
    'anime_genres',
    db.Column(
        "anime_id",
        UUID(as_uuid=True),
        db.ForeignKey('anime_info.anime_id')
    ),
    db.Column(
        "genre_id",
        db.Integer,
        db.ForeignKey('genres.genre_id')
    )
)
